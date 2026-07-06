# ------- IMPORTS -------
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from schemas import SaveResponse
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
    existing_save = get_save_file(save_id, database)
    
    return existing_save