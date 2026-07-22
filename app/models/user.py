from sqlalchemy import Column, String, Integer, Enum
from app.database import Base
import uuid

from app.types.user import GenderType, RoleType

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True)
    login = Column(String, unique=True)
    password_hash = Column(String)

    role = Column(Enum(RoleType), default=RoleType.USER)

    birth_year = Column(Integer)
    gender = Column(Enum(GenderType))
    category = Column(String)