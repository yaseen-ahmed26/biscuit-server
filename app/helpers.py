# ------- IMPORTS -------
from nanoid import generate

from fastapi import status, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models

# ------- SETUP -------
alphanumeric = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

# ------- FUNCTIONS -------
def generate_id(size: int = 5):
    return generate(alphanumeric, size)

async def compare_user_id(target_id: int, current_user_id: int):
    if target_id != current_user_id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "not authorised to delete this user"
        )

async def get_user_by_id(target_id, database: AsyncSession):
    result = await database.execute(
        select(models.User)
        .where(models.User.id == target_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"user with ID '{target_id}' not found"
        )
    
    return user

async def check_username_exists(username: str, database: AsyncSession):
    result = await database.execute(
        select(models.User)
        .where(models.User.username == username)
    )
    existing_username = result.scalars().first()

    if existing_username:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"username '{username}' already exists"
        )
    
async def check_email_exists(email: str, database: AsyncSession):
    result = await database.execute(
        select(models.User)
        .where(models.User.email == email)
    )
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"email '{email}' already exists"
        )