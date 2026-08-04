
import logging

from fastapi import status, HTTPException, Depends, APIRouter, WebSocket, WebSocketDisconnect

from datetime import datetime, UTC, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from typing import Annotated

import asyncio

from app.schemas import CodeResponse, Code, WebsocketMetadata
from app.database import get_database
import app.models as models
from app.security import CurrentUser
from app.helpers import generate_id
from app.constants import LOGIN_CODE_EXPIRATION_MINS, LOGIN_CODE_LENGTH

# ------- SETUP -------
router = APIRouter()
logger = logging.getLogger(__name__)

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
                logger.error("Websocket failed to close for Client %s: %s", login_code, error)


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
    login_code = generate_id(LOGIN_CODE_LENGTH)
    expires_at = datetime.now(UTC) + timedelta(minutes = LOGIN_CODE_EXPIRATION_MINS)

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

    try:
        login_code, expires_at = await generate_websocket_info(database, metadata)

        await manager.connect(login_code, websocket)

        await manager.send_json_message(login_code, {
            "type": "information",
            "login_code": login_code,
        })

        logger.info("Client %s has connected", login_code)

        while True:
            remaining_time = (expires_at - datetime.now(UTC)).total_seconds()
            
            if remaining_time <= 0:
                raise asyncio.TimeoutError()

            message = await asyncio.wait_for(
                websocket.receive_text(), 
                timeout = remaining_time
            )

    except asyncio.TimeoutError:
        logger.info("Client %s has timed out", login_code)

        await manager.send_json_message(login_code, {
            "type": "expired",
            "detail": "websocket has expired"
        })
    except WebSocketDisconnect:
        logger.info("Client %s has disconnected", login_code)
    except Exception as error:
        logger.warning("Client %s has encountered an error: %s", login_code, error)
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
            "owned_upgrades": user.save.owned_upgrades,
            "owned_achievements": user.save.owned_achievements,
            "prestige": user.save.prestige,
            "crumbs": user.save.crumbs,
            "owned_unlocks": user.save.owned_unlocks,
        }
    })
    await asyncio.sleep(0.05)
    await manager.disconnect(existing_code.login_code)
        
    return existing_code