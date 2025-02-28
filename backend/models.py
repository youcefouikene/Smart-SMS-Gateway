from pydantic import BaseModel, EmailStr
from typing import List, Optional

# Validé
class KeywordSettings(BaseModel):
    text: str
    notificationTimes: List[int]

# Validé
class SMSNotificationSettings(BaseModel):
    agendaFields: List[str]
    phoneNumber: str
    keywords: List[KeywordSettings]

# Validé
class User(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    settings: Optional[SMSNotificationSettings] = None

# Validé
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Validé
class UserLogin(BaseModel):
    username: str
    password: str