# ------- IMPORTS -------
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    EmailStr
)

from datetime import datetime
from typing import Any

from app.constants import LOGIN_CODE_LENGTH

# ------- SCHEMAS -------
# Users
class UserBase(BaseModel):
    username: str = Field(min_length = 1, max_length = 30)
    email: EmailStr = Field(max_length = 60)

class UserCreate(UserBase):
    password: str = Field(min_length = 8)

class UserUpdate(BaseModel):
    username: str | None = Field(default = None, min_length = 1, max_length = 30)
    email: EmailStr | None = Field(default = None, max_length = 60)

    password: str | None = Field(default = None, min_length = 8)
    current_password: str | None = Field(default = None)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    username: str
    created_at: datetime

class UserPrivate(UserPublic):
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class RefreshBody(BaseModel):
    refresh_token: str | None = Field(default = None)

# Codes
class Code(BaseModel):
    login_code: str = Field(min_length = LOGIN_CODE_LENGTH, max_length = LOGIN_CODE_LENGTH)

class CodeResponse(BaseModel):
    login_code: str
    os: str
    country: str
    game_id: str
    model_config = ConfigDict(from_attributes = True)

class WebsocketMetadata(BaseModel):
    os: str | None = Field(default = "Unknown", max_length = 25)
    country: str | None = Field(default = "Unknown", max_length = 32)
    game_id: str = Field(max_length = 32)

# Saves
class SaveUpdate(BaseModel):
    save_data: dict[str, Any]
    version_number: float | None = Field(default = None)

class SaveResponse(BaseModel):
    save_id: str   
    game_id: str
    version_number: float | None = Field(default = None)
    last_saved_at: datetime   
    save_data: dict[str, Any]
    model_config = ConfigDict(from_attributes = True)