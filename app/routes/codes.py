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

import asyncio

# ------- SETUP -------
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, login_code, websocket: WebSocket):
        await websocket.accept(headers = None)
        self.active_connections[login_code] = websocket

    async def disconnect(self, login_code: str):
        websocket = self.active_connections.pop(login_code, None)

        if websocket:
            try:
                await websocket.close()
            except Exception as error:
                print(f"An error occurred closing the websocket: {error}")

    async def send_text_message(self, login_code, message: str):
        websocket = self.active_connections.get(login_code)

        if websocket:
            await websocket.send_text(message)

    async def send_json_message(self, login_code, data: str):
        websocket = self.active_connections.get(login_code)

        if websocket:
            await websocket.send_json(data)

manager = ConnectionManager()

# ------- HELPERS -------
async def generate_websocket_info(database: AsyncSession, metadata):
    login_code = generate_id(7)
    expires_at = datetime.now(UTC) + timedelta(minutes = 2)

    new_code = models.Codes(
        login_code = login_code,
        expires_at = expires_at,
        os = metadata.os,
        country = metadata.country
    )

    database.add(new_code)
    await database.commit()

    return login_code, expires_at

# ------- ENDPOINTS -------
@router.websocket(
    "/ws"
)
async def start_websocket(
    websocket: WebSocket,
    database: Annotated[AsyncSession, Depends(get_database)],
    metadata: WebsocketMetadata = Depends()
):
    login_code = None
    conncted = False

    try:
        login_code, expires_at = await generate_websocket_info(database, metadata)

        await manager.connect(login_code, websocket)
        conncted = True

        await manager.send_json_message(login_code, {
            "type": "information",
            "login_code": login_code,
        })

        while True:
            message = await websocket.receive_text()

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as error:
        print(f"An error occurred: {error}")
    finally:
        if login_code is not None:
            result = await database.execute(
                select(models.Codes)
                .where(models.Codes.login_code == login_code)
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

    await manager.send_json_message(existing_code.login_code, {
        "type": "user_data",
        "save_id": user.save.save_id,
        "username": user.username,
        "save": {
            "biscuits": user.save.biscuits,
            "total_biscuits": user.save.total_biscuits,
            "total_playtime": user.save.total_playtime,
            "total_clicks": user.save.total_clicks,
            "bought_upgrades": user.save.bought_upgrades,
            "completed_achievements": user.save.completed_achievements
        }
    })
    await asyncio.sleep(0.05)
    await manager.disconnect(existing_code.login_code)
        
    return existing_code