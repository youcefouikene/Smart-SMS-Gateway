from pydantic import BaseModel, EmailStr
from typing import List, Optional
from .settings import SMSNotificationSettings

# Validé
class User(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    settings: Optional[SMSNotificationSettings] = None
    google_token: Optional[str] = None

# Validé
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Validé
class UserLogin(BaseModel):
    email: str
    password: str