from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from schemas import (
    UserCreate, 
    UserUpdate, 
    UserPrivate, 
    UserSave,
)

from helpers import (
    generate_id,
    compare_user_id,
    get_user_by_id, 
    check_username_exists,
    check_email_exists
)

from database import get_database
import models

from security import (
    hash_password, 
    verify_password,
    CurrentUser
)

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
@router.get(
    "/me", 
    response_model = UserSave
)
def get_current_user(current_user: CurrentUser):
    return current_user

@router.post(
    "",
    response_model = UserSave,
    status_code = status.HTTP_201_CREATED
)
async def create_user(user_info: UserCreate, database: Annotated[AsyncSession, Depends(get_database)]):
    await check_username_exists(user_info.username, database)
    await check_email_exists(user_info.email, database)

    new_user = models.User(
        username = user_info.username,
        email = user_info.email,
        password_hash = hash_password(user_info.password),
    )

    new_save = models.Save(
        save_id = generate_id(32),
        biscuits = 20.0,
        total_biscuits = 0.0,
        total_playtime = 0.0,
        total_clicks = 0,
        bought_upgrades = {},
        completed_achievements = []
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
    await compare_user_id(user_id, current_user.id)
    user = await get_user_by_id(user_id, database)
    
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
    await compare_user_id(user_id, current_user.id)
    user = await get_user_by_id(user_id, database)
    
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
        if updated_info.username == user.username:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"username cannot be the same as your current one"
            )

        await check_username_exists(updated_info.username, database)
        
        user.username = updated_info.username
    
    if updated_info.email is not None:
        if updated_info.email == user.email:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"email cannot be the same as your current one"
            )

        await check_email_exists(updated_info.email, database)

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
    user = await get_user_by_id(user_id, database)

    return user