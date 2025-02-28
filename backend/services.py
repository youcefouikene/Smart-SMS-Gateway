# services.py
from typing import Optional
from database import db
from models import User

def get_user_by_username(username: str) -> Optional[User]:
    user = db.users.find_one({"username": username})
    if user:
        return User(**user)
    return None