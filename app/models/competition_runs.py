from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from app.database import Base
import uuid


class CompetitionRun(Base):
    __tablename__ = "competition_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"))

    name = Column(String(255))
    run_date = Column(DateTime)