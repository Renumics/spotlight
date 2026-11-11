"""Browser origin enforcement and explicitly allowed cross-origin access."""

import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from renumics.spotlight.backend.middlewares.origins import AllowedOriginsMiddleware

APP_ORIGIN = "https://spotlight.example"
PORTAL_ORIGIN = "https://portal.example"


@pytest.fixture
def client() -> TestClient:
    async def endpoint(request: Request) -> JSONResponse:
        return JSONResponse({"method": request.method})

    async def websocket(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json({"connected": True})
        await websocket.close()

    app = Starlette(
        routes=[
            Route("/", endpoint, methods=["GET", "POST", "PUT", "PATCH", "DELETE"]),
            WebSocketRoute("/ws", websocket),
        ],
        middleware=[
            Middleware(
                AllowedOriginsMiddleware,
                allowed_origins=[PORTAL_ORIGIN],
                server_origin=APP_ORIGIN,
            ),
            Middleware(
                CORSMiddleware,
                allow_origins=[PORTAL_ORIGIN],
                allow_credentials=True,
                allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
                allow_headers=["Content-Type"],
            ),
        ],
    )
    return TestClient(app, base_url=APP_ORIGIN)


@pytest.mark.parametrize("origin", [APP_ORIGIN, PORTAL_ORIGIN])
def test_allowed_browser_requests(client: TestClient, origin: str) -> None:
    assert client.put("/", headers={"Origin": origin}).status_code == 200
    with client.websocket_connect("/ws", headers={"Origin": origin}) as websocket:
        assert websocket.receive_json() == {"connected": True}


@pytest.mark.parametrize(
    "origin",
    [
        "https://attacker.example",
        "https://spotlight.example.attacker.example",
        "https://spotlight.example:444",
        "http://spotlight.example",
        "https://portal.example:444",
        "null",
        "https://spotlight.example@attacker.example",
    ],
)
def test_reject_untrusted_origins(client: TestClient, origin: str) -> None:
    assert client.put("/", headers={"Origin": origin}).status_code == 403
    with (
        pytest.raises(WebSocketDisconnect) as error,
        client.websocket_connect("/ws", headers={"Origin": origin}),
    ):
        pytest.fail("An untrusted WebSocket origin was accepted")
    assert error.value.code == 1008


def test_host_header_does_not_define_allowed_origin(client: TestClient) -> None:
    headers = {"Host": "attacker.example", "Origin": "https://attacker.example"}
    assert client.put("/", headers=headers).status_code == 403


def test_native_http_clients_and_missing_websocket_origin(client: TestClient) -> None:
    assert client.put("/").status_code == 200
    assert client.put("/", headers={"Sec-Fetch-Site": "cross-site"}).status_code == 403
    with pytest.raises(WebSocketDisconnect), client.websocket_connect("/ws"):
        pytest.fail("A WebSocket without an Origin was accepted")


def test_cors_only_grants_access_to_configured_origins(client: TestClient) -> None:
    headers = {
        "Origin": PORTAL_ORIGIN,
        "Access-Control-Request-Method": "PUT",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/", headers=headers)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == PORTAL_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"
    response = client.put("/", headers={"Origin": PORTAL_ORIGIN})
    assert response.headers["access-control-allow-origin"] == PORTAL_ORIGIN
    headers["Origin"] = "https://attacker.example"
    response = client.options("/", headers=headers)
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
