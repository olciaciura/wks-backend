import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.models.user import User
from app.utils.security import hash_password
from sqlalchemy.orm import Session
from app.database import SessionLocal
from pydantic import BaseModel

# Sekretny klucz - najlepiej ten sam co używasz do logowania
SECRET_KEY = "LLlDj3X88jnjYUSG8jbwYTl6K4s3xmAMVP4vCdB24F3OIkPbwA" 

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

router = APIRouter(prefix="/password")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

conf = ConnectionConfig(
    MAIL_USERNAME="",           # Zostaw puste
    MAIL_PASSWORD="",           # Zostaw puste
    MAIL_FROM="password@zgloszenia-treningi.pl", # MUSI BYĆ PODANE (adres nadawcy)
    MAIL_PORT=25,               # Domyślny port dla niezaszyfrowanego SMTP
    MAIL_SERVER="postfix", # Host (np. adres IP lub nazwa w Dockerze)
    MAIL_STARTTLS=False,        # Wyłączamy, bo łączymy się wewnątrz własnej sieci
    MAIL_SSL_TLS=False,         # Wyłączamy
    USE_CREDENTIALS=False,      # TO JEST KLUCZOWE: mówi bibliotece, by w ogóle nie próbowała się logować
    VALIDATE_CERTS=False
)

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    
    if user:
        # 1. Tworzymy token
        payload = {
            "sub": str(user.id),
            "exp": datetime.utcnow() + timedelta(minutes=15)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        # 2. Tworzymy link
        reset_link = f"http://localhost:5173/reset-password?token={token}"

        print(f"Reset link for {user.email}: {reset_link}")  # Debug: print the reset link to the console
        
        # 3. Tworzymy treść HTML maila
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <h2 style="color: #00a6e5;">OriSuS - Reset hasła</h2>
            <p>Cześć {user.first_name},</p>
            <p>Otrzymaliśmy prośbę o zresetowanie hasła do Twojego konta (login: <strong>{user.login}</strong>). Kliknij w poniższy przycisk, aby ustawić nowe hasło. Link jest ważny przez 15 minut.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="background-color: #00a6e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Zresetuj hasło</a>
            </div>
            <p style="font-size: 0.85rem; color: #777;">Jeśli przycisk nie działa, skopiuj ten link do przeglądarki:<br>{reset_link}</p>
            <p style="font-size: 0.85rem; color: #777;">Jeśli to nie Ty prosiłeś o zmianę hasła, po prostu zignoruj tę wiadomość.</p>
        </div>
        """

        # 4. Przygotowujemy obiekt wiadomości
        message = MessageSchema(
            subject="Reset hasła do konta OriSuS",
            recipients=[user.email], # Wysyłamy na maila z bazy
            body=html_content,
            subtype=MessageType.html
        )

        # 5. Wysyłamy maila W TLE (nie blokujemy odpowiedzi serwera!)
        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message)

    # Zwracamy odpowiedź natychmiast
    return {"msg": "Jeśli adres email istnieje, wysłano na niego link do zmiany hasła."}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(req.token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.password_hash = hash_password(req.new_password) 
        db.commit()
        
        return {"msg": "Hasło zostało pomyślnie zmienione."}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token wygasł. Wygeneruj nowy link.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Nieprawidłowy token.")