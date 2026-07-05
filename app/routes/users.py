from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from schemas import (
    UserCreate, 
    UserUpdate, 
    UserPublic, 
    UserPrivate, 
    UserSave,
    Token
)

from helpers import generate_id

from database import get_database
import models

from auth import (
    create_access_token, 
    hash_password, 
    verify_password, 
    CurrentUser
)

from config import settings

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.post(
    "/token", 
    response_model = Token
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], database: Annotated[AsyncSession, Depends(get_database)]):
    result = await database.execute(
        select(models.User)
        .where(models.User.email == form_data.username)
    )

    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "incorrect email or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes = settings.access_token_expire_minutes)

    access_token = create_access_token(
        data = {"sub": str(user.id)},
        expires_delta = access_token_expires,
    )

    return Token(access_token = access_token, token_type = "bearer")

@router.get(
    "/me", 
    response_model = UserPrivate
)
def get_current_user(current_user: CurrentUser):
    return current_user

@router.post(
    "",
    response_model = UserSave,
    status_code = status.HTTP_201_CREATED
)
async def create_user(user_info: UserCreate, database: Annotated[AsyncSession, Depends(get_database)]):
    result = await database.execute(
        select(models.User)
        .where(models.User.username == user_info.username)
    )
    existing_username = result.scalars().first()

    if existing_username:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"username '{user_info.username}' already exists"
        )
    
    result = await database.execute(
        select(models.User)
        .where(models.User.email == user_info.email)
    )
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"email '{user_info.email}' already exists"
        )

    new_user = models.User(
        username = user_info.username,
        email = user_info.email,
        password_hash = hash_password(user_info.password),
    )

    new_save = models.Save(
        level = 1
    )

    new_user.save = new_save

    database.add(new_user)
    await database.commit()
    await database.refresh(new_user, attribute_names = ["save"])

    return new_user

@router.delete(
    "/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
async def delete_user(user_id: int, current_user: CurrentUser, database: Annotated[AsyncSession, Depends(get_database)]):
    if user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "not authorised to delete this user"
        )
    
    result = await database.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"user with ID '{user_id}' not found"
        )
    
    await database.delete(user)
    await database.commit()

@router.patch(
    "/{user_id}",
    response_model = UserPrivate,
    status_code = status.HTTP_200_OK
)
async def update_user(
    user_id: int, 
    updated_info: UserUpdate,
    current_user: CurrentUser,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    print(updated_info)

    if user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "not authorised to update this user"
        )

    result = await database.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"user with ID '{user_id}' not found"
        )
    
    if not updated_info.current_password:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "current password is required to change your password"
        )
        
    if not verify_password(updated_info.current_password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "incorrect password"
        )
    
    if updated_info.password is not None:
        user.password_hash = hash_password(updated_info.password)
    
    if updated_info.username is not None:
        print(updated_info.username)
        print(user.username)

        if updated_info.username == user.username:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"username cannot be the same as your current one"
            )

        result = await database.execute(
            select(models.User)
            .where(models.User.username == updated_info.username)
        )
        existing_username = result.scalars().first()

        if existing_username:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"username '{updated_info.username}' already exists"
            )
        
        user.username = updated_info.username
    
    if updated_info.email is not None:
        if updated_info.email == user.email:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"email cannot be the same as your current one"
            )

        result = await database.execute(
            select(models.User)
            .where(models.User.email == updated_info.email)
        )
        existing_email = result.scalars().first()

        if existing_email:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"email '{updated_info.email}' already exists"
            )

        user.email = updated_info.email

    await database.commit()
    await database.refresh(user)
    
    return user

@router.get(
    "",
    response_model = list[UserPrivate]
)
async def get_all_users(database: Annotated[AsyncSession, Depends(get_database)]):
    result = await database.execute(select(models.User))
    users = result.scalars().all()

    return users

@router.get(
    "/{user_id}",
    response_model = UserPrivate
)
async def get_specific_user(user_id: int, database: Annotated[AsyncSession, Depends(get_database)]):
    result = await database.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )
    user = result.scalars().first()

    if user: return user
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = f"user with ID '{user_id}' not found"
    )