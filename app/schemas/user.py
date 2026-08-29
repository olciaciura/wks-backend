from pydantic import BaseModel
from app.types.user import GenderType, RoleType

class UserCreate(BaseModel):
    email: str
    login: str
    password: str
    first_name: str | None = None
    last_name: str | None = None
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

class UserUpdate(BaseModel):
    login: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_year: int | None = None
    gender: GenderType | None = None
    category: str | None = None
class LoginResponse(BaseModel):
    user_id: str
    login: str
    role: RoleType
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    birth_year: int | None = None
    gender: GenderType | None = None
    category: str | None = None 

    class Config:
        orm_mode = True
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str