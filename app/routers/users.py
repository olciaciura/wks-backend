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