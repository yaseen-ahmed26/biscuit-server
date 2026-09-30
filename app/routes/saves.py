# ------- IMPORTS -------
from fastapi import Depends, APIRouter, HTTPException, status
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.schemas import SaveResponse, SaveUpdate
from app.database import get_database
import app.models as models
from app.security import CurrentUser

from app.constants import MAX_AMOUNT_BISCUITS_CLICK, AVERAGE_CLICK_SPEED_SECOND, BISCUIT_BUFFER, MAX_SESSION_LENGTH, SAVE_ID_LENGTH
from app.helpers import generate_id

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.get(
    "/{game_id}/me",
    response_model = SaveResponse
)
async def get_save_data(
    game_id: str,
    current_user: CurrentUser, 
    database: Annotated[AsyncSession, Depends(get_database)]
):    
    result = await database.execute(
        select(models.Save)
        .where(models.Save.user_id == current_user.id)
        .where(models.Save.game_id == game_id)
    )
    save = result.scalars().first()

    if save:
        return save

    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = f"No save found for User {current_user.id} for Game '{game_id}'"
    )

@router.put(
    "/{game_id}/me",
    response_model = SaveResponse
)
async def update_save(
    game_id: str,
    current_user: CurrentUser, 
    new_save: SaveUpdate,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    result = await database.execute(
        select(models.Save)
        .where(models.Save.user_id == current_user.id)
        .where(models.Save.game_id == game_id)
    )
    save = result.scalars().first()

    if save:
        if game_id == "biscuit":
            seconds_elapsed = int((datetime.now(UTC) - save.last_saved_at.replace(tzinfo = UTC)).total_seconds())
            total_session = min(seconds_elapsed, MAX_SESSION_LENGTH)
            max_allowed_gain = total_session * MAX_AMOUNT_BISCUITS_CLICK * AVERAGE_CLICK_SPEED_SECOND * BISCUIT_BUFFER
            
            incoming_biscuits = new_save.save_data.get("biscuits", 0)

            if incoming_biscuits > max_allowed_gain:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = "biscuits exceed the max theoretical gain, player may have cheated"
                )

        save.save_data = new_save.save_data
        save.last_saved_at = datetime.now(UTC)

        if new_save.version_number is not None:
            save.version_number = new_save.version_number

    else:
        save = models.Save(
            user_id = current_user.id,
            game_id = game_id,
            save_id = generate_id(SAVE_ID_LENGTH),
            save_data = new_save.save_data,
            version_number = new_save.version_number or 0.0,
            last_saved_at = datetime.now(UTC)
        )
        database.add(save)

    await database.commit()
    await database.refresh(save)
    return save


# @router.get(
#     "/{save_id}",
# )
# async def get_stranger_save(
#     save_id: str,
#     database: Annotated[AsyncSession, Depends(get_database)]
# ):
#     existing_save = await get_save_file(save_id, database)
#     user = await get_user_by_id(existing_save.user_id, database)

#     return {
#         "total_biscuits": existing_save.total_biscuits,
#         "total_clicks": existing_save.total_clicks,
#         "total_playtime": existing_save.total_playtime,
#         "player_username": user.username
#     }