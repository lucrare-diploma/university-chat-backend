# schemas/user.py
from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    password_hash: str

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
