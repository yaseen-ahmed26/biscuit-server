# ------- IMPORTS -------
from fastapi import Depends, APIRouter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.schemas import SaveResponse, SaveUpdate, LeaderboardUser
from app.database import get_database
import app.models as models
from app.helpers import get_save_file, get_user_by_id
from app.security import CurrentUser

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
    existing_save = await get_save_file(current_user.save.save_id, database)
    
    return existing_save

@router.put(
    "/me",
    response_model = SaveResponse
)
async def update_save(
    current_user: CurrentUser, 
    new_save: SaveUpdate,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    existing_save = await get_save_file(current_user.save.save_id, database)

    update_data = new_save.model_dump(exclude_unset = True)

    for field, value in update_data.items():
        setattr(existing_save, field, value)

    await database.commit()
    await database.refresh(existing_save)
    
    return existing_save