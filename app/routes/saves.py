# ------- IMPORTS -------
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from schemas import SaveResponse, SaveUpdate
from database import get_database
import models

from helpers import get_save_file

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.get(
    "/{save_id}",
    response_model = SaveResponse
)
async def get_save_data(save_id: str, database: Annotated[AsyncSession, Depends(get_database)]):
    existing_save = await get_save_file(save_id, database)
    
    return existing_save

@router.put(
    "/{save_id}",
    response_model = SaveResponse
)
async def update_save(
    save_id: str, 
    new_save: SaveUpdate,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    existing_save = await get_save_file(save_id, database)

    update_data = new_save.model_dump(exclude_unset = True)

    for field, value in update_data.items():
        setattr(existing_save, field, value)

    await database.commit()
    await database.refresh(existing_save)
    
    return existing_save