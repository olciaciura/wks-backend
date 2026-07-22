from pydantic import BaseModel

from app.types.user import GenderType, RoleType

class UserCreate(BaseModel):
    email: str
    login: str
    password: str
    role: RoleType = RoleType.USER
    birth_year: int | None = None
    gender: GenderType | None = None
    category: str | None = None


class UserLogin(BaseModel):
    login: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    login: str
    role: RoleType


class LoginResponse(BaseModel):
    user_id: str
    login: str
    role: RoleType

    class Config:
        orm_mode = True