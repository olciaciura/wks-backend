import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("BASE_DB_HOST")
DB_PORT = os.getenv("BASE_DB_PORT", "3306")
DB_USER = os.getenv("BASE_DB_USER")
DB_PASSWORD = os.getenv("BASE_DB_PASSWORD")
DB_NAME = os.getenv("BASE_DB_NAME")

if DB_HOST:
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    connect_args = {}
else:
    DATABASE_URL = "sqlite:///./test.db"  # lokalny rozwój bez MySQL
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()