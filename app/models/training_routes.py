from sqlalchemy import Column, ForeignKey, Numeric, String
from app.database import Base
import uuid


class TrainingRoutes(Base):
    __tablename__ = "training_routes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("events.id"))

    name = Column(String)
    description = Column(String)
    distance = Column(Numeric)