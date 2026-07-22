from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from app.database import Base
import uuid


class CompetitionRunSelection(Base):
    __tablename__ = "competition_run_selections"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    response_id = Column(String, ForeignKey("user_event_responses.id"))
    run_id = Column(String, ForeignKey("competition_runs.id"))

    participates = Column(Boolean, default=False)