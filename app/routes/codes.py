from fastapi import status, HTTPException, Depends, APIRouter, WebSocket, WebSocketDisconnect

from datetime import datetime, UTC, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from typing import Annotated

from schemas import CodeResponse, Code, WebsocketMetadata
from database import get_database
import models

from auth import CurrentUser
from helpers import generate_id

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

    async def send_text_message(self, session_id, message: str):
        websocket = self.active_connections.get(session_id)

        if websocket:
            await websocket.send_text(message)

    async def send_json_message(self, session_id, data: str):
        websocket = self.active_connections.get(session_id)

        if websocket:
            await websocket.send_json(data)

manager = ConnectionManager()

# ------- HELPERS -------
async def generate_websocket_info(database: AsyncSession, metadata):
    session_id = generate_id(21)
    login_code = generate_id(7)
    expires_at = datetime.now(UTC) + timedelta(minutes = 2)

    new_code = models.Codes(
        session_id = session_id,
        login_code = login_code,
        expires_at = expires_at,
        os = metadata.os,
        country = metadata.country
    )

    database.add(new_code)
    await database.commit()

    return session_id, login_code, expires_at

# ------- ENDPOINTS -------
@router.websocket(
    "/ws"
)
async def start_websocket(
    websocket: WebSocket,
    database: Annotated[AsyncSession, Depends(get_database)],
    metadata: WebsocketMetadata = Depends()
):
    session_id = None
    conncted = False

    try:
        session_id, login_code, expires_at = await generate_websocket_info(database, metadata)

        await manager.connect(session_id, websocket)
        conncted = True

        await manager.send_json_message(session_id, {
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

        if session_id is not None:
            result = await database.execute(
                select(models.Codes)
                .where(models.Codes.session_id == session_id)
            )
            existing_code = result.scalars().first()

            if existing_code:
                await database.delete(existing_code)
                await database.commit()

@router.post(
    "/verify",
    response_model = CodeResponse,
    status_code = status.HTTP_200_OK
)
async def verify(
    code: Code,
    current_user: CurrentUser,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    result = await database.execute(
        select(models.Codes)
        .where(models.Codes.login_code == code.login_code)
    )
    existing_code = result.scalars().first()

    if not existing_code:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"'{code.login_code}' is invalid"
        )
    
    result = await database.execute(
        select(models.User)
        .options(selectinload(models.User.save))
        .where(models.User.id == current_user.id)
    )
    user = result.scalars().first()

    await manager.send_json_message(existing_code.session_id, {
        "username": user.username,
        "save_id": user.save.local_id,
        "save": {
            "level": user.save.level
        }
    })
    manager.disconnect(existing_code.session_id)

    await database.delete(existing_code)
    await database.commit()
        
    return existing_code