"""
HTTP requests for external media and layout URLs.
"""

import os
import socket
import sys
from ipaddress import IPv6Address, ip_address, ip_network
from typing import Any, Literal
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from urllib3.exceptions import ConnectTimeoutError, NewConnectionError
from urllib3.util.connection import create_connection

from renumics.spotlight.__version__ import __version__
from renumics.spotlight.settings import settings

headers = {
    # https://meta.wikimedia.org/wiki/User-Agent_policy
    "User-Agent": f"SpotlightBot/{__version__} (https://github.com/Renumics/spotlight)"
}


class BlockedMediaURL(ValueError):
    """An external URL resolves to a network that Spotlight may not access."""


def _address_allowed(address: str) -> bool:
    ip = ip_address(address)
    if isinstance(ip, IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    if ip.is_unspecified or ip.is_multicast:
        return False
    if any(ip in ip_network(network) for network in settings.allowed_internal_networks):
        return True
    # These cloud platform endpoints can be classified as global addresses.
    if ip in (ip_address("168.63.129.16"), ip_address("192.0.0.192")):
        return False
    # Transition mechanisms can encode non-public IPv4 destinations inside
    # otherwise global-looking IPv6 addresses.
    if isinstance(ip, IPv6Address) and (
        ip.sixtofour is not None
        or ip.teredo is not None
        or ip in ip_network("64:ff9b::/96")
    ):
        return False
    return ip.is_global


def _connect(connection: HTTPConnection) -> socket.socket:
    try:
        addresses = list(
            dict.fromkeys(
                str(result[4][0])
                for result in socket.getaddrinfo(
                    connection.host, connection.port, type=socket.SOCK_STREAM
                )
            )
        )
    except OSError as error:
        raise NewConnectionError(
            connection, "Could not resolve media hostname"
        ) from error
    if not addresses or not all(_address_allowed(address) for address in addresses):
        raise BlockedMediaURL(
            "External URL resolves to a blocked network. Configure "
            "SPOTLIGHT_ALLOWED_INTERNAL_NETWORKS to allow an internal media server."
        )

    last_error: OSError = OSError("No media server address available")
    for address in addresses:
        try:
            # Connect to the validated numeric address, without resolving the
            # hostname again. The original hostname remains in Host and TLS SNI.
            sock = create_connection(
                (address, connection.port),
                connection.timeout,
                source_address=connection.source_address,
                socket_options=connection.socket_options,
            )
        except OSError as error:
            last_error = error
        else:
            sys.audit(
                "http.client.connect", connection, connection.host, connection.port
            )
            return sock
    if isinstance(last_error, socket.timeout):
        raise ConnectTimeoutError(
            connection, "Media connection timed out"
        ) from last_error
    raise NewConnectionError(
        connection, "Could not connect to media server"
    ) from last_error


class _MediaHTTPConnection(HTTPConnection):
    def _new_conn(self) -> socket.socket:
        return _connect(self)


class _MediaHTTPSConnection(HTTPSConnection):
    def _new_conn(self) -> socket.socket:
        return _connect(self)


class _MediaHTTPPool(HTTPConnectionPool):
    ConnectionCls = _MediaHTTPConnection


class _MediaHTTPSPool(HTTPSConnectionPool):
    ConnectionCls = _MediaHTTPSConnection


class _MediaAdapter(HTTPAdapter):
    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: Any
    ) -> None:
        super().init_poolmanager(connections, maxsize, block, **pool_kwargs)
        # Do not modify urllib3's shared pool class mapping.
        self.poolmanager.pool_classes_by_scheme = {
            "http": _MediaHTTPPool,
            "https": _MediaHTTPSPool,
        }


def fetch_url(
    url: str,
    *,
    method: Literal["GET", "HEAD"] = "GET",
    timeout: float = 30,
    stream: bool = False,
) -> requests.Response:
    """Fetch an HTTP(S) URL, checking every new connection and redirect hop."""
    if urlsplit(url).scheme not in ("http", "https"):
        raise BlockedMediaURL("Only HTTP(S) media URLs are supported")
    with requests.Session() as session:
        # Environment proxies resolve destinations themselves, bypassing local
        # address checks. Also avoid attaching credentials from .netrc.
        session.trust_env = False
        session.verify = (
            os.environ.get("REQUESTS_CA_BUNDLE")
            or os.environ.get("CURL_CA_BUNDLE")
            or True
        )
        session.headers.update(headers)
        session.mount("http://", _MediaAdapter())
        session.mount("https://", _MediaAdapter())
        return session.request(
            method,
            url,
            timeout=timeout,
            stream=stream,
            allow_redirects=method != "HEAD",
        )
