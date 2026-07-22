from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.competition_details import CompetitionDetails
from app.models.competition_responses import CompetitionResponse
from app.models.competition_run_selection import CompetitionRunSelection
from app.models.competition_runs import CompetitionRun
from app.models.events import Event
from app.models.food_options import FoodOption
from app.models.training_details import TrainingDetails
from app.models.training_responses import TrainingResponse
from app.models.training_routes import TrainingRoutes
from app.models.user import User
from app.models.user_event_response import UserEventResponse
from app.schemas.event import EventCreateRequest, SubmitEventResponseRequest
from app.types.events import EventType
from app.types.user_event_response import StatusType as ResponseStatusType

router = APIRouter(prefix="/events", tags=["events"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _response_label(status: ResponseStatusType | None) -> str:
    if status == ResponseStatusType.REJECTED:
        return "nie_jade"
    if status == ResponseStatusType.FILLED:
        return "uzupelnione"
    return "nieuzupelnione"


@router.post("/")
def create_event(payload: EventCreateRequest, db: Session = Depends(get_db)):
    event = Event(
        type=payload.type,
        title=payload.title,
        description=payload.description,
        date_from=payload.date_from,
        date_to=payload.date_to,
        signup_open_date=payload.signup_open_date,
        signup_close_date=payload.signup_close_date,
        status=payload.status,
    )
    db.add(event)
    db.flush()

    if payload.type == EventType.TRAINING:
        details = payload.training_details
        if details is None:
            raise HTTPException(status_code=400, detail="training_details are required for training event")

        db.add(
            TrainingDetails(
                event_id=event.id,
                type=details.type,
                meeting_time=details.meeting_time,
                meeting_location_desc=details.meeting_location_desc,
                meeting_location_link=details.meeting_location_link,
                start_time=details.start_time,
                start_location_desc=details.start_location_desc,
                start_location_link=details.start_location_link,
                transport_available=details.transport_available,
            )
        )

        for route in payload.training_routes:
            db.add(
                TrainingRoutes(
                    event_id=event.id,
                    name=route.name,
                    description=route.description,
                    distance=route.distance,
                )
            )

    if payload.type == EventType.COMPETITION:
        details = payload.competition_details
        if details is None:
            raise HTTPException(status_code=400, detail="competition_details are required for competition event")

        db.add(
            CompetitionDetails(
                event_id=event.id,
                competition_name=details.competition_name,
                transport_available=details.transport_available,
                departure_time=details.departure_time,
                departure_location_desc=details.departure_location_desc,
                departure_location_link=details.departure_location_link,
                accomodation_available=details.accomodation_available,
                accomodation_location_desc=details.accomodation_location_desc,
                accomodation_location_link=details.accomodation_location_link,
                food_available=details.food_available,
                food_vege_available=details.food_vege_available,
                series_signup=details.series_signup,
            )
        )

        for run in payload.competition_runs:
            db.add(CompetitionRun(event_id=event.id, name=run.name, run_date=run.run_date))

        for option in payload.food_options:
            db.add(
                FoodOption(
                    event_id=event.id,
                    date=option.date,
                    breakfast=option.breakfast,
                    lunch=option.lunch,
                    dinner=option.dinner,
                    supper=option.supper,
                )
            )

    db.commit()
    db.refresh(event)

    return {"event_id": event.id, "type": event.type.value, "title": event.title}


@router.get("/user/{user_id}")
def list_user_events(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rows = (
        db.query(Event, UserEventResponse)
        .outerjoin(
            UserEventResponse,
            and_(UserEventResponse.event_id == Event.id, UserEventResponse.user_id == user_id),
        )
        .order_by(Event.signup_open_date.desc())
        .all()
    )

    response = []
    for event, user_response in rows:
        response.append(
            {
                "event_id": event.id,
                "event_name": event.title,
                "event_type": event.type.value,
                "signup_open_date": event.signup_open_date,
                "signup_close_date": event.signup_close_date,
                "event_status": event.status.value,
                "user_response_status": _response_label(user_response.status if user_response else None),
            }
        )

    return response


@router.post("/{event_id}/responses")
def submit_event_response(event_id: str, payload: SubmitEventResponseRequest, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    root_response = (
        db.query(UserEventResponse)
        .filter(UserEventResponse.event_id == event_id, UserEventResponse.user_id == payload.user_id)
        .first()
    )

    if root_response is None:
        root_response = UserEventResponse(event_id=event_id, user_id=payload.user_id)
        db.add(root_response)
        db.flush()

    root_response.status = payload.status
    root_response.needs_transport = payload.needs_transport
    root_response.self_transport = payload.self_transport
    root_response.can_take_people = payload.can_take_people
    root_response.comment = payload.comment
    root_response.submitted_at = datetime.utcnow()

    if event.type == EventType.TRAINING:
        training_data = payload.training
        if training_data is None:
            raise HTTPException(status_code=400, detail="Training response payload is required")

        training_response = (
            db.query(TrainingResponse).filter(TrainingResponse.response_id == root_response.id).first()
        )
        if training_response is None:
            training_response = TrainingResponse(response_id=root_response.id)
            db.add(training_response)

        training_response.selected_route_id = training_data.selected_route_id

    if event.type == EventType.COMPETITION:
        competition_data = payload.competition
        if competition_data is None:
            raise HTTPException(status_code=400, detail="Competition response payload is required")

        competition_response = (
            db.query(CompetitionResponse)
            .filter(CompetitionResponse.response_id == root_response.id)
            .first()
        )
        if competition_response is None:
            competition_response = CompetitionResponse(response_id=root_response.id)
            db.add(competition_response)

        competition_response.needs_accommodation = competition_data.needs_accommodation
        competition_response.wants_food = competition_data.wants_food
        competition_response.wants_vege = competition_data.wants_vege

        db.query(CompetitionRunSelection).filter(
            CompetitionRunSelection.response_id == root_response.id
        ).delete()

        for run in competition_data.run_selections:
            db.add(
                CompetitionRunSelection(
                    response_id=root_response.id,
                    run_id=run.run_id,
                    participates=run.participates,
                )
            )

    db.commit()

    return {"response_id": root_response.id, "status": root_response.status.value}


@router.get("/{event_id}")
def get_event_details(event_id: str, user_id: str | None = None, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    payload = {
        "event": {
            "id": event.id,
            "type": event.type.value,
            "title": event.title,
            "description": event.description,
            "date_from": event.date_from,
            "date_to": event.date_to,
            "signup_open_date": event.signup_open_date,
            "signup_close_date": event.signup_close_date,
            "status": event.status.value,
        },
        "options": {},
        "user_response": None,
    }

    if event.type == EventType.TRAINING:
        details = db.query(TrainingDetails).filter(TrainingDetails.event_id == event_id).first()
        routes = db.query(TrainingRoutes).filter(TrainingRoutes.event_id == event_id).all()
        payload["options"] = {
            "transport_available": details.transport_available if details else False,
            "meeting_time": details.meeting_time if details else None,
            "meeting_location_desc": details.meeting_location_desc if details else None,
            "meeting_location_link": details.meeting_location_link if details else None,
            "start_time": details.start_time if details else None,
            "start_location_desc": details.start_location_desc if details else None,
            "start_location_link": details.start_location_link if details else None,
            "training_type": details.type.value if details else None,
            "routes": [
                {
                    "id": route.id,
                    "name": route.name,
                    "description": route.description,
                    "distance": float(route.distance),
                }
                for route in routes
            ],
        }

    if event.type == EventType.COMPETITION:
        details = db.query(CompetitionDetails).filter(CompetitionDetails.event_id == event_id).first()
        runs = db.query(CompetitionRun).filter(CompetitionRun.event_id == event_id).all()
        food_options = db.query(FoodOption).filter(FoodOption.event_id == event_id).all()
        payload["options"] = {
            "transport_available": details.transport_available if details else False,
            "departure_time": details.departure_time if details else None,
            "departure_location_desc": details.departure_location_desc if details else None,
            "departure_location_link": details.departure_location_link if details else None,
            "accomodation_available": details.accomodation_available if details else False,
            "accomodation_location_desc": details.accomodation_location_desc if details else None,
            "accomodation_location_link": details.accomodation_location_link if details else None,
            "food_available": details.food_available if details else False,
            "food_vege_available": details.food_vege_available if details else False,
            "series_signup": details.series_signup if details else False,
            "runs": [{"id": run.id, "name": run.name, "run_date": run.run_date} for run in runs],
            "food_schedule": [
                {
                    "date": option.date,
                    "breakfast": option.breakfast,
                    "lunch": option.lunch,
                    "dinner": option.dinner,
                    "supper": option.supper,
                }
                for option in food_options
            ],
        }

    if user_id:
        root_response = (
            db.query(UserEventResponse)
            .filter(UserEventResponse.event_id == event_id, UserEventResponse.user_id == user_id)
            .first()
        )
        if root_response:
            payload["user_response"] = {
                "status": root_response.status.value,
                "needs_transport": root_response.needs_transport,
                "self_transport": root_response.self_transport,
                "can_take_people": int(root_response.can_take_people),
                "comment": root_response.comment,
                "submitted_at": root_response.submitted_at,
            }

            if event.type == EventType.TRAINING:
                training_response = (
                    db.query(TrainingResponse)
                    .filter(TrainingResponse.response_id == root_response.id)
                    .first()
                )
                payload["user_response"]["training"] = {
                    "selected_route_id": training_response.selected_route_id if training_response else None
                }

            if event.type == EventType.COMPETITION:
                competition_response = (
                    db.query(CompetitionResponse)
                    .filter(CompetitionResponse.response_id == root_response.id)
                    .first()
                )
                run_selections = (
                    db.query(CompetitionRunSelection)
                    .filter(CompetitionRunSelection.response_id == root_response.id)
                    .all()
                )
                payload["user_response"]["competition"] = {
                    "needs_accommodation": competition_response.needs_accommodation if competition_response else False,
                    "wants_food": competition_response.wants_food if competition_response else False,
                    "wants_vege": competition_response.wants_vege if competition_response else False,
                    "run_selections": [
                        {"run_id": run.run_id, "participates": run.participates} for run in run_selections
                    ],
                }

    return payload
