from pydantic import ConfigDict
from pydantic.main import BaseModel
from pydantic.networks import EmailStr


class UserBase(BaseModel):
    email: EmailStr | None = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    email: EmailStr
    password: str


class User(UserBase):
    id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    hashed_password: str
