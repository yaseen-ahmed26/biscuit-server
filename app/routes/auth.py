# ------- IMPORTS -------
from fastapi import status, HTTPException, Depends, APIRouter, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from schemas import Token

from database import get_database
import models

from security import (
    create_access_token, 
    verify_password,
    create_refresh_token,
)

from config import settings

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.post(
    "/login", 
    response_model = Token
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    database: Annotated[AsyncSession, Depends(get_database)],
    response: Response
):
    result = await database.execute(
        select(models.User)
        .where(models.User.email == form_data.username)
    )

    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "incorrect email or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes = settings.access_token_expire_minutes)

    access_token = create_access_token(
        data = {"sub": str(user.id)},
        expires_delta = access_token_expires,
    )

    plain_token, hashed_token = create_refresh_token()
    expires_at = datetime.now() + timedelta(days = 7)

    response.set_cookie(        
		key = "refresh_token",        
		value = plain_token,       
		secure = True,        
		httponly = True,
        path = "/api/auth/refresh",
        max_age = 7 * 24 * 3600
    )

    new_session = models.Session(
        user_id = user.id,
        token_hash = hashed_token,
        expires_at = expires_at,  
        expired = False
    )

    database.add(new_session)
    await database.commit()

    return Token(access_token = access_token, token_type = "bearer")

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