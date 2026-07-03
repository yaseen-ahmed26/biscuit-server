# ------- IMPORTS -------

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    EmailStr
)

from datetime import datetime

# ------- SCHEMAS -------
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
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class Code(BaseModel):
    code: str = Field(min_length = 7, max_length = 7)

class CodeResponse(BaseModel):
    session_id: str
    login_code: str