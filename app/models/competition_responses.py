from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from app.database import Base
import uuid


class CompetitionResponse(Base):
    __tablename__ = "competition_responses"

    response_id = Column(String, ForeignKey("user_event_responses.id"), primary_key=True)
    
    needs_accommodation = Column(Boolean, default=False)

    wants_food = Column(Boolean, default=False)
    wants_vege = Column(Boolean, default=False)