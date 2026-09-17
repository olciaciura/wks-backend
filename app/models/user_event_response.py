from sqlalchemy import Boolean, Column, ForeignKey, Numeric, String, DateTime, Enum, Text, UniqueConstraint
from app.database import Base
import uuid

from app.types.user_event_response import StatusType

class UserEventResponse(Base):
    __tablename__ = "user_event_responses"
    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_user_event_response_event_user"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"))
    user_id = Column(String(36), ForeignKey("users.id"))

    status = Column(Enum(StatusType), default=StatusType.PENDING)

    needs_transport = Column(Boolean, default=False)
    self_transport = Column(Boolean, default=False)
    can_take_people = Column(Numeric, default=0)

    comment = Column(Text, nullable=True)

    submitted_at = Column(DateTime)