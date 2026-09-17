from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.routers import events, password, users

# Import models so SQLAlchemy registers all tables in Base.metadata.
from app.models.user import User  # noqa: F401
from app.models.events import Event  # noqa: F401
from app.models.training_details import TrainingDetails  # noqa: F401
from app.models.training_routes import TrainingRoutes  # noqa: F401
from app.models.food_options import FoodOption  # noqa: F401
from app.models.competition_details import CompetitionDetails  # noqa: F401
from app.models.competition_runs import CompetitionRun  # noqa: F401
from app.models.user_event_response import UserEventResponse  # noqa: F401
from app.models.training_responses import TrainingResponse  # noqa: F401
from app.models.competition_responses import CompetitionResponse  # noqa: F401
from app.models.competition_run_selection import CompetitionRunSelection  # noqa: F401


def cleanup_duplicate_user_event_responses() -> None:
    db = SessionLocal()
    try:
        rows = (
            db.query(UserEventResponse)
            .order_by(
                UserEventResponse.event_id.asc(),
                UserEventResponse.user_id.asc(),
                UserEventResponse.submitted_at.desc().nullslast(),
                UserEventResponse.id.desc(),
            )
            .all()
        )

        seen = set()
        for row in rows:
            key = (row.event_id, row.user_id)
            if key in seen:
                db.delete(row)
            else:
                seen.add(key)

        db.commit()

        try:
            db.execute(
                text(
                    "CREATE UNIQUE INDEX uq_user_event_response_event_user ON user_event_responses (event_id, user_id)"
                )
            )
            db.commit()
        except Exception:
            db.rollback()
    finally:
        db.close()


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://zgloszenia-treningi.pl",
    "https://zgloszenia-treningi.pl",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(events.router)
app.include_router(password.router)
Base.metadata.create_all(bind=engine)
cleanup_duplicate_user_event_responses()

@app.get("/")
def read_root():
    return {"message": "API działa 🚀"}
