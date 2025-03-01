# crud.py
from typing import List, Optional
from database import db
from models import UserCreate, SMSNotificationSettings, KeywordSettings
from services import get_user_by_username  # <-- Changé ici
from auth import get_password_hash

# Opérations CRUD

# def create_user(user: UserCreate):
#     hashed_password = get_password_hash(user.password)
#     user_dict = user.model_dump()
#     user_dict["hashed_password"] = hashed_password
#     user_dict.pop("password")
#     db.users.insert_one(user_dict)
#     return user_dict


def create_user(user: UserCreate):
    hashed_password = get_password_hash(user.password)

    default_settings = SMSNotificationSettings(
        agendaFields=[],  # Aucun champ d'agenda au départ
        phoneNumber="",  # Numéro de téléphone vide
        keywords=[]  # Liste vide de mots-clés
    )

    user_dict = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "settings": default_settings.model_dump()  # Convertir en dict pour MongoDB
    }

    db.users.insert_one(user_dict)
    return user_dict


def update_user_settings(username: str, settings: SMSNotificationSettings):
    db.users.update_one({"username": username}, {"$set": {"settings": settings.dict()}})
    return settings

def add_keyword_to_user(username: str, keyword: KeywordSettings):
    user = get_user_by_username(username)
    if not user or not user.settings:
        return None

    settings = user.settings
    settings.keywords.append(keyword)
    update_user_settings(username, settings)
    return settings

def add_notification_time_to_keyword(username: str, keyword: str, notification_time: int):
    user = get_user_by_username(username)
    if not user or not user.settings:
        return None

    settings = user.settings
    for kw in settings.keywords:
        if kw.text == keyword:
            if notification_time in kw.notificationTimes:
                return None  # Éviter les doublons
            kw.notificationTimes.append(notification_time)
            break
    else:
        return None

    update_user_settings(username, settings)
    return settings

def delete_keyword_from_user(username: str, keyword: str):
    user = get_user_by_username(username)
    if not user or not user.settings:
        return None

    settings = user.settings
    settings.keywords = [kw for kw in settings.keywords if kw.text != keyword]
    update_user_settings(username, settings)
    return settings

def delete_notification_time_from_keyword(username: str, keyword: str, notification_time: int):
    user = get_user_by_username(username)
    if not user or not user.settings:
        return None

    settings = user.settings
    for kw in settings.keywords:
        if kw.text == keyword:
            kw.notificationTimes = [t for t in kw.notificationTimes if t != notification_time]
            break
    else:
        return None

    update_user_settings(username, settings)
    return settings

def get_all_users():
    return list(db.users.find({}, {"_id": 0, "hashed_password": 0}))

def get_user_settings(username: str):
    user = get_user_by_username(username)
    if not user or not user.settings:
        return None
    return user.settings

def get_all_settings():
    users = get_all_users()
    return [user.get("settings", {}) for user in users]

def update_user_phone_number(username: str, new_phone_number: str):
    user = get_user_by_username(username)
    if not user or not user.settings:
        return None

    settings = user.settings
    settings.phoneNumber = new_phone_number
    update_user_settings(username, settings)
    return settings

def update_user_agenda_fields(username: str, new_fields: List[str]):
    user = get_user_by_username(username)
    if not user or not user.settings:
        return None

    settings = user.settings
    settings.agendaFields = new_fields
    update_user_settings(username, settings)
    return settings