from sqlalchemy import Boolean, Column, ForeignKey, Numeric, String, DateTime, Enum
from app.database import Base
import uuid

from app.types.user_event_response import StatusType

class UserEventResponse(Base):
    __tablename__ = "user_event_responses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("events.id"))
    user_id = Column(String, ForeignKey("users.id"))

    status = Column(Enum(StatusType), default=StatusType.PENDING)
    
    needs_transport = Column(Boolean, default=False)
    self_transport = Column(Boolean, default=False)
    can_take_people = Column(Numeric, default=0)

    comment = Column(String)

    submitted_at = Column(DateTime)