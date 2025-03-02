from fastapi import HTTPException, Header
import os
import jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def get_current_user(authorization: str = Header(...)):
    """
    Extrage și decodează tokenul JWT din header-ul 'Authorization'.
    Așteaptă ca header-ul să fie de forma: "Bearer <token>".
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Payload-ul conține, de exemplu, user_id și rol
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
