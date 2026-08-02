from datetime import date, datetime, time

from pydantic import BaseModel

from app.types.events import EventType, StatusType as EventStatusType
from app.types.training_details import TrainingType
from app.types.user_event_response import StatusType as ResponseStatusType


class TrainingRouteInput(BaseModel):
    name: str
    description: str | None = None
    distance: float


class TrainingDetailsInput(BaseModel):
    type: TrainingType = TrainingType.SPRINT
    meeting_time: time | None = None
    meeting_location_desc: str | None = None
    meeting_location_link: str | None = None
    start_time: time | None = None
    start_location_desc: str | None = None
    start_location_link: str | None = None
    transport_available: bool = False


class FoodOptionInput(BaseModel):
    date: datetime
    breakfast: bool = False
    lunch: bool = False
    dinner: bool = False
    supper: bool = False


class CompetitionRunInput(BaseModel):
    name: str
    run_date: datetime


class CompetitionDetailsInput(BaseModel):
    competition_name: str
    transport_available: bool = False
    departure_time: datetime | None = None
    departure_location_desc: str | None = None
    departure_location_link: str | None = None
    accomodation_available: bool = False
    accomodation_location_desc: str | None = None
    accomodation_location_link: str | None = None
    food_available: bool = False
    food_vege_available: bool = False
    series_signup: bool = False


class EventCreateRequest(BaseModel):
    type: EventType
    title: str
    description: str | None = None
    date_from: date
    date_to: date
    signup_open_date: datetime
    signup_close_date: datetime

class CompetitionCreateRequest(EventCreateRequest):
    competition_details: CompetitionDetailsInput | None = None
    competition_runs: list[CompetitionRunInput] = []
    food_options: list[FoodOptionInput] = []

class TrainingCreateRequest(EventCreateRequest):
    training_details: TrainingDetailsInput | None = None
    training_routes: list[TrainingRouteInput] = []

class TrainingResponseInput(BaseModel):
    selected_route_id: str | None = None


class CompetitionRunSelectionInput(BaseModel):
    run_id: str
    participates: bool = True


class CompetitionResponseInput(BaseModel):
    needs_accommodation: bool = False
    wants_food: bool = False
    wants_vege: bool = False
    run_selections: list[CompetitionRunSelectionInput] = []


class SubmitEventResponseRequest(BaseModel):
    user_id: str
    status: ResponseStatusType = ResponseStatusType.FILLED
    needs_transport: bool = False
    self_transport: bool = False
    can_take_people: int = 0
    comment: str | None = None

class SubmitTrainingResponseRequest(SubmitEventResponseRequest):
    training: TrainingResponseInput

class SubmitCompetitionResponseRequest(SubmitEventResponseRequest):
    competition: CompetitionResponseInput