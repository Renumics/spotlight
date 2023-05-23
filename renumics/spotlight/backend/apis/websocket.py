"""
Endpoints for websocket communication.
"""

from fastapi import APIRouter, WebSocket


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Handle all websocket connections and dispatch all incoming messages.
    """
    connection = websocket.app.websocket_manager.create_connection(websocket)
    await connection.listen()
