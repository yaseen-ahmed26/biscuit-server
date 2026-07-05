# ------- IMPORTS -------
from fastapi import status, HTTPException, Depends, APIRouter


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from schemas import SaveResponse
from database import get_database
import models

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.get(
    "/{save_id}",
    response_model = SaveResponse
)
async def get_save_data(save_id: str, database: Annotated[AsyncSession, Depends(get_database)]):
    result = await database.execute(
        select(models.Save)
        .where(models.Save.save_id == save_id)
    )
    existing_save = result.scalars().first()

    if not existing_save:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"'no save with ID {save_id}' was found"
        )
    
    return existing_save