from sqlalchemy import Boolean, Column, Date, String, DateTime, Enum, ForeignKey, Time
from app.database import Base
import uuid

from app.types.training_details import TrainingType


class TrainingDetails(Base):
    __tablename__ = "training_details"

    event_id = Column(String(36), ForeignKey("events.id"), primary_key=True)
    type = Column(Enum(TrainingType), default=TrainingType.SPRINT)

    meeting_time = Column(Time)
    meeting_location_desc = Column(String(255))
    meeting_location_link = Column(String(255))

    start_time = Column(Time)
    start_location_desc = Column(String(255))
    start_location_link = Column(String(255))

    transport_available = Column(Boolean, default=False)