"""Origin checks for browser requests, including WebSocket handshakes."""

from urllib.parse import urlsplit

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from renumics.spotlight.settings import normalize_origin


class AllowedOriginsMiddleware:
    """Allow the server's own origin and explicitly configured extra origins."""

    def __init__(
        self,
        app: ASGIApp,
        allowed_origins: list[str],
        server_origin: str | None = None,
    ) -> None:
        self.app = app
        self.allowed_origins = set(allowed_origins)
        self.server_origin = server_origin

    def _is_allowed(self, origin: str, scope: Scope) -> bool:
        try:
            origin = normalize_origin(origin)
        except (ValueError, UnicodeError):
            return False
        if origin in self.allowed_origins:
            return True

        server_origin = self.server_origin
        if server_origin is None:
            # ASGI's socket address is independent of client-supplied Host and
            # forwarded headers. Named public/proxy origins must be configured.
            server = scope.get("server")
            if server is None:
                return False
            host, port = server
            host = f"[{host}]" if ":" in host else host
            scheme = "https" if scope["scheme"] in ("https", "wss") else "http"
            server_origin = f"{scheme}://{host}:{port}"
        try:
            server_origin = normalize_origin(server_origin)
        except (ValueError, UnicodeError):
            return False
        if origin == server_origin:
            return True

        # The local viewer can be opened through either loopback spelling.
        local_hosts = {"localhost", "127.0.0.1"}
        server_url, origin_url = urlsplit(server_origin), urlsplit(origin)
        return (
            server_url.hostname in local_hosts
            and origin_url.hostname in local_hosts
            and server_url.scheme == origin_url.scheme
            and server_url.port == origin_url.port
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        websocket = scope["type"] == "websocket"
        unsafe_http = scope["type"] == "http" and scope["method"] not in (
            "GET",
            "HEAD",
            "OPTIONS",
        )
        if websocket or unsafe_http:
            headers = Headers(scope=scope)
            origins = headers.getlist("origin")
            if not origins and not websocket:
                # Preserve non-browser API clients. Browser requests identifying
                # themselves as cross-site must still supply an allowed origin.
                allowed = headers.get("sec-fetch-site") in (None, "same-origin")
            else:
                allowed = len(origins) == 1 and self._is_allowed(origins[0], scope)
            if not allowed:
                if websocket:
                    await send({"type": "websocket.close", "code": 1008})
                else:
                    await JSONResponse(
                        {"detail": "Origin is not allowed"}, status_code=403
                    )(scope, receive, send)
                return
        await self.app(scope, receive, send)
