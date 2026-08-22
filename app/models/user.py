from sqlalchemy import Column, String, Integer, Enum
from app.database import Base
import uuid

from app.types.user import GenderType, RoleType

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True)
    login = Column(String(255), unique=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    password_hash = Column(String(255))

    role = Column(Enum(RoleType), default=RoleType.USER)

    birth_year = Column(Integer)
    gender = Column(Enum(GenderType))
    category = Column(String(255))