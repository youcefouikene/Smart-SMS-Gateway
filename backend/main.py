from typing import List
from fastapi import FastAPI, HTTPException, Depends
from models import UserCreate, UserLogin, SMSNotificationSettings, KeywordSettings
from crud import (
    create_user, get_user_by_username, update_user_settings,
    add_keyword_to_user, add_notification_time_to_keyword,
    delete_keyword_from_user, delete_notification_time_from_keyword,
    get_all_users, get_user_settings, get_all_settings,
    update_user_phone_number, update_user_agenda_fields
)
from auth import get_current_user, get_password_hash, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models import User
from datetime import timedelta


app = FastAPI()

# Routes

@app.post("/register")
async def register(user: UserCreate):
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data["hashed_password"] = hashed_password
    create_user(UserCreate(**user_data))
    return {"message": "Utilisateur créé avec succès"}


@app.post("/login")
async def login(user: UserLogin):
    db_user = authenticate_user(user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Identifiants invalides")

    # Générer le token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )

    # Retourner le token au lieu du message "Connexion réussie"
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/add-keyword")
async def add_keyword(
    keyword: str,
    first_notification_time: int,
    current_user: User = Depends(get_current_user)
):
    new_keyword = KeywordSettings(text=keyword, notificationTimes=[first_notification_time])
    settings = add_keyword_to_user(current_user.username, new_keyword)
    if not settings:
        raise HTTPException(status_code=404, detail="Utilisateur ou paramètres non trouvés")
    return {"message": "Mot-clé ajouté avec succès"}

@app.post("/add-notification-time")
async def add_notification_time(
    keyword: str,
    notification_time: int,
    current_user: User = Depends(get_current_user)
):
    settings = add_notification_time_to_keyword(current_user.username, keyword, notification_time)
    if not settings:
        raise HTTPException(status_code=404, detail="Mot-clé non trouvé")
    return {"message": "Temps de notification ajouté avec succès"}

@app.delete("/delete-keyword")
async def delete_keyword(
    keyword: str,
    current_user: User = Depends(get_current_user)
):
    settings = delete_keyword_from_user(current_user.username, keyword)
    if not settings:
        raise HTTPException(status_code=404, detail="Mot-clé non trouvé")
    return {"message": "Mot-clé supprimé avec succès"}

@app.delete("/delete-notification-time")
async def delete_notification_time(
    keyword: str,
    notification_time: int,
    current_user: User = Depends(get_current_user)
):
    settings = delete_notification_time_from_keyword(current_user.username, keyword, notification_time)
    if not settings:
        raise HTTPException(status_code=404, detail="Mot-clé ou temps de notification non trouvé")
    return {"message": "Temps de notification supprimé avec succès"}

@app.get("/users")
async def get_users():
    users = get_all_users()
    return {"users": users}

@app.get("/user-settings/{username}")
async def get_user_settings(username: str):
    settings = get_user_settings(username)
    if not settings:
        raise HTTPException(status_code=404, detail="Utilisateur ou paramètres non trouvés")
    return settings

@app.get("/all-settings")
async def get_all_settings():
    settings = get_all_settings()
    return {"all_settings": settings}

@app.put("/update-phone")
async def update_phone(
    new_phone_number: str,
    current_user: User = Depends(get_current_user)
):
    settings = update_user_phone_number(current_user.username, new_phone_number)
    if not settings:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Numéro de téléphone mis à jour avec succès"}

@app.put("/update-agenda-fields")
async def update_agenda_fields(
    new_fields: List[str],
    current_user: User = Depends(get_current_user)
):
    settings = update_user_agenda_fields(current_user.username, new_fields)
    if not settings:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Champs de l'agenda mis à jour avec succès"}