from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import events, users

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
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "API działa 🚀"}
