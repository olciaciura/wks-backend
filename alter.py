from sqlalchemy import text
from app.database import SessionLocal

db = SessionLocal()

db.execute(text("""
    ALTER TABLE events
    ADD COLUMN location TEXT
"""))

db.commit()
db.close()