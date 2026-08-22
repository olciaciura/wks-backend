from sqlalchemy import Column, ForeignKey, Numeric, String
from app.database import Base
import uuid


class TrainingRoutes(Base):
    __tablename__ = "training_routes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"))

    name = Column(String(255))
    description = Column(String(255))
    distance = Column(Numeric)