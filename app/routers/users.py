from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import LoginResponse, UserCreate, UserLogin, UserResponse
from app.types.user import RoleType
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/users")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.email == user.email) | (User.login == user.login)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email or login already exists")

    new_user = User(
        email=user.email,
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        password_hash=hash_password(user.password),
        role=RoleType.USER,
        birth_year=user.birth_year,
        gender=user.gender,
        category=user.category,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=LoginResponse)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == credentials.login).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login or password")

    return LoginResponse(user_id=user.id, login=user.login, role=user.role)

@router.post("/role", response_model=UserResponse)
def change_user_role(user_id: str, new_role: RoleType, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user

from sqlalchemy import text  # <-- To jest ważne do czystego SQL
from app.database import get_db # Zaimportuj swoją funkcję pobierającą sesję bazy

# Dodaj to gdzieś w swoim kodzie:
@router.get("/uruchom-migracje-awaryjna")
def migrate_db(db: Session = Depends(get_db)):
    try:
        # Wykonujemy czysty kod SQL, który dodaje kolumnę
        # ZMIEŃ 'users' na nazwę swojej tabeli i 'nowe_pole' na nazwę swojej kolumny!
        # Jeśli to tekst, dodaj VARCHAR(255). Jeśli co innego, np. INT, BOOLEAN.
        sql_query = text("ALTER TABLE users ADD COLUMN first_name VARCHAR(255), ADD COLUMN last_name VARCHAR(255);")
        
        db.execute(sql_query)
        db.commit()
        return {"status": "sukces", "wiadomosc": "Kolumna została pomyślnie dodana do bazy!"}
    
    except Exception as e:
        # Jeśli kolumna już istnieje, wyrzuci błąd, co też chcemy zobaczyć
        return {"status": "blad", "szczegoly": str(e)}
