# services.py
from typing import Optional
from db.database import db
from models.user import User

def get_user_by_username(username: str) -> Optional[User]:
    user = db.users.find_one({"username": username})
    if user:
        return User(**user)
    return None

def get_user_by_email(email: str) -> Optional[User]:
    user = db.users.find_one({"email": email})
    if user:
        return User(**user)
    return None