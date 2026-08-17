import json
from datetime import date, datetime, time, timezone
from pathlib import Path

from app.database import Base, SessionLocal, engine
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
from app.types.events import EventType, StatusType as EventStatusType
from app.types.training_details import TrainingType
from app.types.user import GenderType, RoleType
from app.types.user_event_response import StatusType as ResponseStatusType
from app.utils.security import hash_password



ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "FRONTEND_TEST_DATA.json"


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(value)


def parse_time(value: str | None) -> time | None:
    if value is None:
        return None
    if "T" in value:
        return parse_datetime(value).time()
    return time.fromisoformat(value)


def clear_all(db):
    db.query(CompetitionRunSelection).delete()
    db.query(CompetitionResponse).delete()
    db.query(TrainingResponse).delete()
    db.query(UserEventResponse).delete()
    db.query(FoodOption).delete()
    db.query(CompetitionRun).delete()
    db.query(CompetitionDetails).delete()
    db.query(TrainingRoutes).delete()
    db.query(TrainingDetails).delete()
    db.query(Event).delete()
    db.query(User).delete()
    db.commit()


def load_test_data():
    Base.metadata.create_all(bind=engine)

    with DATA_FILE.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    db = SessionLocal()
    try:
        clear_all(db)

        for u in payload.get("users", []):
            db.add(
                User(
                    id=u["id"],
                    email=u["email"],
                    login=u["login"],
                    password_hash=hash_password(u.get("password", "Test123!")),
                    role=RoleType(u["role"]),
                    birth_year=u.get("birth_year"),
                    gender=GenderType(u["gender"]) if u.get("gender") else None,
                    category=u.get("category"),
                )
            )

        for e in payload.get("events", []):
            event = Event(
                id=e["id"],
                type=EventType(e["type"]),
                title=e["title"],
                description=e.get("description"),
                date_from=parse_date(e["date_from"]),
                date_to=parse_date(e["date_to"]),
                signup_open_date=parse_datetime(e["signup_open_date"]),
                signup_close_date=parse_datetime(e["signup_close_date"]),
                status=EventStatusType(e["status"]),
            )
            db.add(event)

            if e["type"] == EventType.TRAINING.value:
                details = e.get("training_details")
                if details:
                    db.add(
                        TrainingDetails(
                            event_id=e["id"],
                            type=TrainingType(details["type"]),
                            meeting_time=parse_time(details.get("meeting_time")),
                            meeting_location_desc=details.get("meeting_location_desc"),
                            meeting_location_link=details.get("meeting_location_link"),
                            start_time=parse_time(details.get("start_time")),
                            start_location_desc=details.get("start_location_desc"),
                            start_location_link=details.get("start_location_link"),
                            transport_available=details.get("transport_available", False),
                        )
                    )

                for route in e.get("training_routes", []):
                    db.add(
                        TrainingRoutes(
                            id=route["id"],
                            event_id=e["id"],
                            name=route["name"],
                            description=route.get("description"),
                            distance=route["distance"],
                        )
                    )

            if e["type"] == EventType.COMPETITION.value:
                details = e.get("competition_details")
                if details:
                    db.add(
                        CompetitionDetails(
                            event_id=e["id"],
                            competition_name=details["competition_name"],
                            transport_available=details.get("transport_available", False),
                            departure_time=parse_datetime(details.get("departure_time")),
                            departure_location_desc=details.get("departure_location_desc"),
                            departure_location_link=details.get("departure_location_link"),
                            accomodation_available=details.get("accomodation_available", False),
                            accomodation_location_desc=details.get("accomodation_location_desc"),
                            accomodation_location_link=details.get("accomodation_location_link"),
                            food_available=details.get("food_available", False),
                            food_vege_available=details.get("food_vege_available", False),
                            series_signup=details.get("series_signup", False),
                        )
                    )

                for run in e.get("competition_runs", []):
                    db.add(
                        CompetitionRun(
                            id=run["id"],
                            event_id=e["id"],
                            name=run["name"],
                            run_date=parse_datetime(run["run_date"]),
                        )
                    )

                for option in e.get("food_options", []):
                    db.add(
                        FoodOption(
                            id=option["id"],
                            event_id=e["id"],
                            date=parse_datetime(option["date"]),
                            breakfast=option.get("breakfast", False),
                            lunch=option.get("lunch", False),
                            dinner=option.get("dinner", False),
                            supper=option.get("supper", False),
                        )
                    )

        for r in payload.get("responses", []):
            root_response = UserEventResponse(
                id=r["id"],
                event_id=r["event_id"],
                user_id=r["user_id"],
                status=ResponseStatusType(r["status"]),
                needs_transport=r.get("needs_transport", False),
                self_transport=r.get("self_transport", False),
                can_take_people=r.get("can_take_people", 0),
                comment=r.get("comment"),
                submitted_at=parse_datetime(r.get("submitted_at")),
            )
            db.add(root_response)

            training = r.get("training")
            if training is not None:
                db.add(
                    TrainingResponse(
                        response_id=r["id"],
                        selected_route_id=training.get("selected_route_id"),
                    )
                )

            competition = r.get("competition")
            if competition is not None:
                db.add(
                    CompetitionResponse(
                        response_id=r["id"],
                        needs_accommodation=competition.get("needs_accommodation", False),
                        wants_food=competition.get("wants_food", False),
                        wants_vege=competition.get("wants_vege", False),
                    )
                )

                for selected_run in competition.get("run_selections", []):
                    db.add(
                        CompetitionRunSelection(
                            response_id=r["id"],
                            run_id=selected_run["run_id"],
                            participates=selected_run.get("participates", False),
                        )
                    )

        db.commit()
        print("Seed finished successfully.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_test_data()