from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

PASSWORD_MAX_LENGTH = 128


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, max_length=255)
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=PASSWORD_MAX_LENGTH)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=PASSWORD_MAX_LENGTH)
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    name: str | None = None
    is_active: bool
    is_superuser: bool


class UserInDB(UserRead):
    hashed_password: str


User = UserRead
