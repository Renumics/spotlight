"""External media cannot connect to internal networks without explicit access."""

import io
import socket
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import av
import pytest

from renumics.spotlight import requests as media_requests
from renumics.spotlight.io.audio import read_audio
from renumics.spotlight.requests import BlockedMediaURL, fetch_url
from renumics.spotlight.settings import settings


@pytest.fixture(autouse=True)
def isolated_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "allowed_internal_networks", [])


@pytest.fixture
def media_server() -> Iterator[tuple[str, list[tuple[str, str]]]]:
    hits: list[tuple[str, str]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            hits.append((self.path, self.headers["Host"]))
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header(
                    "Location", f"http://127.0.0.2:{server.server_port}/secret"
                )
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(b"synthetic-media")

        def log_message(self, *args: Any) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", hits
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize(
    "host",
    [
        "127.0.0.1",
        "10.0.0.1",
        "172.16.0.1",
        "192.168.0.1",
        "169.254.169.254",
        "168.63.129.16",
        "192.0.0.192",
        "100.100.100.200",
        "0.0.0.0",
        "224.0.0.1",
        "[::1]",
        "[fd00:ec2::254]",
        "[fe80::1]",
        "[::ffff:127.0.0.1]",
        "[64:ff9b::7f00:1]",
        "2130706433",
        "0x7f000001",
    ],
)
def test_internal_addresses_are_blocked(host: str) -> None:
    with pytest.raises(BlockedMediaURL):
        fetch_url(f"http://{host}/", timeout=1)


def test_private_server_needs_explicit_access(
    media_server: tuple[str, list[tuple[str, str]]], monkeypatch: pytest.MonkeyPatch
) -> None:
    url, hits = media_server
    with pytest.raises(BlockedMediaURL):
        fetch_url(url)
    assert hits == []
    monkeypatch.setattr(settings, "allowed_internal_networks", ["127.0.0.1/32"])
    with fetch_url(url, stream=True) as response:
        assert response.raw.read() == b"synthetic-media"
    assert len(hits) == 1


def test_redirect_destination_is_checked(
    media_server: tuple[str, list[tuple[str, str]]], monkeypatch: pytest.MonkeyPatch
) -> None:
    url, hits = media_server
    monkeypatch.setattr(settings, "allowed_internal_networks", ["127.0.0.1/32"])
    with pytest.raises(BlockedMediaURL):
        fetch_url(url + "/redirect")
    assert [path for path, _ in hits] == ["/redirect"]


def test_public_dns_is_pinned_and_host_header_preserved(
    media_server: tuple[str, list[tuple[str, str]]], monkeypatch: pytest.MonkeyPatch
) -> None:
    url, hits = media_server
    port = int(url.rsplit(":", 1)[1])
    real_resolve = socket.getaddrinfo
    real_connect = media_requests.create_connection
    lookups: list[str] = []
    connections: list[tuple[str, int]] = []

    def resolve(host: str, *args: Any, **kwargs: Any) -> Any:
        if host == "media.example":
            lookups.append(host)
            address = "93.184.216.34" if len(lookups) == 1 else "127.0.0.1"
            return real_resolve(address, *args, **kwargs)
        return real_resolve(host, *args, **kwargs)

    def connect(address: tuple[str, int], *args: Any, **kwargs: Any) -> socket.socket:
        connections.append(address)
        return real_connect(("127.0.0.1", port), *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    monkeypatch.setattr(media_requests, "create_connection", connect)
    response = fetch_url(f"http://media.example:{port}/")
    assert response.content == b"synthetic-media"
    assert lookups == ["media.example"]
    assert connections == [("93.184.216.34", port)]
    assert hits == [("/", f"media.example:{port}")]


def test_mixed_public_private_dns_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    real_resolve = socket.getaddrinfo

    def resolve(_host: str, *args: Any, **kwargs: Any) -> Any:
        return real_resolve("93.184.216.34", *args, **kwargs) + real_resolve(
            "127.0.0.1", *args, **kwargs
        )

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    with pytest.raises(BlockedMediaURL):
        fetch_url("http://media.example/")


def test_environment_proxy_cannot_bypass_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://93.184.216.34:3128")
    monkeypatch.setenv("NO_PROXY", "")
    with pytest.raises(BlockedMediaURL):
        fetch_url("http://169.254.169.254/")


def test_audio_playlist_cannot_fetch_nested_urls(
    media_server: tuple[str, list[tuple[str, str]]],
) -> None:
    url, hits = media_server
    playlist = (
        "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n"
        f"#EXTINF:10,\n{url}/segment.ts\n#EXT-X-ENDLIST\n"
    )
    with pytest.raises(av.error.FFmpegError):
        read_audio(io.BytesIO(playlist.encode()))
    assert hits == []
