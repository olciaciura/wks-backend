from sqlalchemy import Column, Date, String, DateTime, Enum
from app.database import Base
import uuid

from app.types.events import EventType, StatusType

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(Enum(EventType), default=EventType.TRAINING)

    title = Column(String)
    description = Column(String)

    date_from = Column(Date)
    date_to = Column(Date)

    signup_open_date = Column(DateTime)
    signup_close_date = Column(DateTime)

    status = Column(Enum(StatusType), default=StatusType.OPEN)