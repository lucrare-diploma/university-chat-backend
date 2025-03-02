from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import timedelta, datetime
import os
import jwt
from passlib.context import CryptContext
from app.database import get_connection, release_connection

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Configurare passlib pentru bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setări JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY is not set in the environment variables!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Schema pentru cererea de autentificare
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Schema pentru răspunsul cu token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=TokenResponse)
def login(login_req: LoginRequest):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        # Caută utilizatorul după email
        cursor.execute("SELECT id, password_hash FROM users WHERE email = %s;", (login_req.email,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        user_id, password_hash = user
        
        # Verifică parola
        if not pwd_context.verify(login_req.password, password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Creează tokenul JWT pentru orice utilizator (rol poate fi extins dacă este nevoie)
        token_data = {"user_id": user_id, "role": "user"}
        access_token = create_access_token(data=token_data)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)
