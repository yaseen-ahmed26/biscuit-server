# ------- IMPORTS -------
from fastapi import Depends, APIRouter, HTTPException, status
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.schemas import SaveResponse, SaveUpdate, LeaderboardUser
from app.database import get_database
import app.models as models
from app.helpers import get_save_file, get_user_by_id
from app.security import CurrentUser

from app.constants import MAX_AMOUNT_BISCUITS_CLICK, AVERAGE_CLICK_SPEED_SECOND, BISCUIT_BUFFER, MAX_SESSION_LENGTH

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.get(
    "/leaderboard",
    response_model = list[LeaderboardUser]
)
async def get_leaderboard(
    database: Annotated[AsyncSession, Depends(get_database)],
    stat: str = "total_biscuits", 
    amount: int = 5
):
    stat_column = getattr(models.Save, stat)
    
    result = await database.execute(
        select(models.Save)
        .order_by(stat_column.desc())
        .limit(amount)
    )

    top_saves = result.scalars().all()

    for save in top_saves:
        user = await get_user_by_id(save.user_id, database)
        save.username = user.username

    return top_saves

@router.get(
    "/me",
    response_model = SaveResponse
)
async def get_save_data(
    current_user: CurrentUser, 
    database: Annotated[AsyncSession, Depends(get_database)]
):    
    return current_user.save

@router.put(
    "/me",
    response_model = SaveResponse
)
async def update_save(
    current_user: CurrentUser, 
    new_save: SaveUpdate,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    existing_save = current_user.save

    seconds_elapsed = int((datetime.now(UTC) - existing_save.last_saved_at.replace(tzinfo = UTC)).total_seconds())
    total_session = min(seconds_elapsed, MAX_SESSION_LENGTH)

    max_allowed_gain = total_session * MAX_AMOUNT_BISCUITS_CLICK * AVERAGE_CLICK_SPEED_SECOND * BISCUIT_BUFFER

    if new_save.biscuits > max_allowed_gain:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "biscuits exceed the max theoretical gain, player may have cheated"
        )

    update_data = new_save.model_dump(exclude_unset = True)

    for field, value in update_data.items():
        setattr(existing_save, field, value)

    existing_save.last_saved_at = datetime.now(UTC)

    await database.commit()
    await database.refresh(existing_save)
    
    return existing_save