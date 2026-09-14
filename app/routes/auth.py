# ------- IMPORTS -------
from fastapi import status, HTTPException, Depends, APIRouter, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm

from datetime import datetime, timedelta, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.database import get_database
import app.models as models
from app.security import (
    create_access_token, 
    verify_password,
    create_refresh_token,
    hash_refresh_token,
    set_cookies
)
from app.config import settings
from app.schemas import RefreshBody

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.post(
    "/login", 
    status_code = status.HTTP_200_OK
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

    plain_refresh, hashed_refresh, refresh_expires, access_token = await set_cookies(user.id, response)

    new_session = models.Session(
        user_id = user.id,
        token_hash = hashed_refresh,
        expires_at = refresh_expires,  
        expired = False
    )

    database.add(new_session)
    await database.commit()

@router.post(
    "/refresh",
    status_code = status.HTTP_200_OK
)
async def get_new_token(
    database: Annotated[AsyncSession, Depends(get_database)],
    response: Response,
    refresh_body: RefreshBody = None,
    refresh_token: Annotated[str | None, Cookie()] = None
):
    token = None
    
    if refresh_token is None and refresh_body is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "no refresh token provided"
        )

    if not refresh_body is None and not refresh_body.refresh_token is None:
        token = refresh_body.refresh_token
    elif not refresh_token is None:
        token = refresh_token

    hashed_token = hash_refresh_token(token)
    
    result = await database.execute(
        select(models.Session)
        .where(models.Session.token_hash == hashed_token)
    )

    stored_token = result.scalars().first()

    if not stored_token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "refresh token does not exist"
        )

    if stored_token.expired:
        result = await database.execute(
            select(models.Session)
            .where(models.Session.user_id == stored_token.user_id)
        )
        
        stored_user_tokens = result.scalars().all()

        for t in stored_user_tokens:
            await database.delete(t)
        
        await database.commit()

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "refresh token already used"
        )

    expires_at = stored_token.expires_at
    
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    if expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "refresh token is expired"
        )

    plain_refresh, hashed_refresh, refresh_expires, access_token = await set_cookies(stored_token.user_id, response)

    new_session = models.Session(
        user_id = stored_token.user_id,
        token_hash = hashed_refresh,
        expires_at = refresh_expires,  
        expired = False
    )

    stored_token.expired = True

    database.add(new_session)
    await database.commit()

    return {
        "access_token": access_token,
        "refresh_token": plain_refresh
    }

@router.post(
    "/logout",
)
async def logout(
    response: Response,
    database: Annotated[AsyncSession, Depends(get_database)],
    refresh_token: Annotated[str | None, Cookie()] = None
):
    hashed_token = hash_refresh_token(refresh_token)
        
    result = await database.execute(
        select(models.Session)
        .where(models.Session.token_hash == hashed_token)
    )

    stored_token = result.scalars().first()

    if stored_token:
        await database.delete(stored_token)
        await database.commit()

    response.delete_cookie(
        key = "access_token",
        secure = True,        
        httponly = True,
        path = "/",
    )

    response.delete_cookie(
        key = "refresh_token",
        secure = True,        
        httponly = True,
        path = "/",
    )