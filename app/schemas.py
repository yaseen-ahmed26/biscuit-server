# ------- IMPORTS -------

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    EmailStr
)

from datetime import datetime
from constants import LOGIN_CODE_LENGTH

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

class UserSave(UserPrivate):
    save: "SaveBase"

class Token(BaseModel):
    access_token: str
    token_type: str

# Codes
class Code(BaseModel):
    login_code: str = Field(min_length = LOGIN_CODE_LENGTH, max_length = LOGIN_CODE_LENGTH)

class CodeResponse(BaseModel):
    login_code: str
    os: str
    country: str

class WebsocketMetadata(BaseModel):
    os: str | None = Field(default = "Unknown", max_length = 25)
    country: str | None = Field(default = "Unknown", max_length = 32)

# Saves
class GameSave(BaseModel):
    biscuits: float
    total_biscuits: float
    total_playtime: float
    total_clicks: int
    owned_upgrades: dict[str, int]
    owned_achievements: list[str]
    prestige: int
    crumbs: int
    owned_unlocks: list[str]

class SaveBase(GameSave):
    model_config = ConfigDict(from_attributes = True)

    save_id: str

class SaveUpdate(GameSave):
    pass

class SaveResponse(SaveBase):
    pass

class LeaderboardUser(BaseModel):
    total_biscuits: float
    username: str

UserSave.model_rebuild()