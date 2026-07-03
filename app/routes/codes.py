from fastapi import status, HTTPException, Depends, APIRouter

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from schemas import CodeResponse, Code
from database import get_database
import models

from auth import CurrentUser

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.post(
    "/verify", 
)
async def verify(
    code: Code,
    current_user: CurrentUser,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    return {"message": f"code you put was {code}"}