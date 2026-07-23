# ------- IMPORTS -------
from fastapi import Depends, APIRouter, Cookie

from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from database import get_database

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.post(
    "/refresh",
)
async def get_new_token(refresh_token: Annotated[str | None, Cookie()], database: Annotated[AsyncSession, Depends(get_database)]):
    pass

@router.post(
    "/logout",
)
async def revoke_refresh_token(database: Annotated[AsyncSession, Depends(get_database)]):
    pass