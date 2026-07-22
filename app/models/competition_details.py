from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from app.database import Base
import uuid


class CompetitionDetails(Base):
    __tablename__ = "competition_details"

    event_id = Column(String, ForeignKey("events.id"), primary_key=True)

    competition_name = Column(String)

    transport_available = Column(Boolean, default=False)
    departure_time = Column(DateTime)
    departure_location_desc = Column(String)
    departure_location_link = Column(String)

    accomodation_available = Column(Boolean, default=False)
    accomodation_location_desc = Column(String)
    accomodation_location_link = Column(String)

    food_available = Column(Boolean, default=False)
    food_vege_available = Column(Boolean, default=False)

    series_signup = Column(Boolean, default=False)