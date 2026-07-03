from fastapi import status, HTTPException, Depends, APIRouter, WebSocket, WebSocketDisconnect

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from schemas import CodeResponse, Code
from database import get_database
import models

from auth import CurrentUser

# ------- SETUP -------
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id, websocket: WebSocket):
        await websocket.accept(headers = None)
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id, message: str):
        websocket = self.active_connections.get(session_id)

        if websocket:
            await websocket.send_text(message)

manager = ConnectionManager()

# ------- HELPERS -------
async def generate_websocket_info(database):
    return "ABCD123", "ABCJF83893K43", datetime.now()

# ------- ENDPOINTS -------
@router.websocket(
    "/ws"
)
async def start_websocket(
    websocket: WebSocket,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    session_id = None
    conncted = False

    try:
        login_code, session_id, expires_at = await generate_websocket_info(database)

        await manager.connect(session_id, websocket)
        conncted = True

        await websocket.send_json({
            "login_code": login_code,
            "session_id": session_id
        })

        while True:
            message = await websocket.receive_text()

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as error:
        print(f"An error occurred: {error}")
    finally:
        if conncted and session_id is not None:
            manager.disconnect(session_id)     

@router.post(
    "/verify", 
)
async def verify(
    code: Code,
    current_user: CurrentUser,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    return {"message": f"code you put was {code}"}