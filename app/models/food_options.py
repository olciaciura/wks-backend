from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from app.database import Base
import uuid


class FoodOption(Base):
    __tablename__ = "food_options"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"))

    date = Column(DateTime)

    breakfast = Column(Boolean, default=False)
    lunch = Column(Boolean, default=False)
    dinner = Column(Boolean, default=False)
    supper = Column(Boolean, default=False)