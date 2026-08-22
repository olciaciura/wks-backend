from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from app.database import Base
import uuid


class TrainingResponse(Base):
    __tablename__ = "training_responses"

    response_id = Column(String(36), ForeignKey("user_event_responses.id"), primary_key=True)
    selected_route_id = Column(String(36), ForeignKey("training_routes.id"))

