import base64
import pickle
from typing import List
import uuid
from fastapi import FastAPI, HTTPException, Depends
from services import get_user_by_email
from models.registration import RegistrationComplete, RegistrationInitResponse
from models.user import UserCreate, UserLogin, User
from models.settings import SMSNotificationSettings, KeywordSettings
from crud import (
    create_user, get_user_by_username, update_user_settings,
    add_keyword_to_user, add_notification_time_to_keyword,
    delete_keyword_from_user, delete_notification_time_from_keyword,
    get_all_users, get_user_settings, get_all_settings,
    update_user_phone_number, update_user_agenda_fields
)
from auth import get_current_user, get_password_hash, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware
from google_auth_oauthlib.flow import InstalledAppFlow
from db.database import db




app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL de votre frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly'
]

pending_registrations = {}
oauth_flows = {}


# Routes


@app.post("/register/init", response_model=RegistrationInitResponse)
async def register_init(user: UserCreate):
    # Vérifier si l'utilisateur existe déjà
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
    
    # Vérifier si l'email existe déjà
    existing_email = get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Adresse email déjà utilisée")
    
    # Créer le flux OAuth
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    
    # Générer l'URL d'autorisation
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    # Générer un ID unique pour cette inscription
    registration_id = str(uuid.uuid4())
    
    # Stocker le flow en mémoire
    oauth_flows[registration_id] = flow
    
    # Stocker les informations d'inscription en attente (sans le flow)
    pending_registrations[registration_id] = {
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "created_at": datetime.now(timezone.utc)
    }
    
    return RegistrationInitResponse(
        registration_id=registration_id,
        auth_url=auth_url,
        message=f"Veuillez vous connecter avec l'adresse e-mail {user.email}"
    )


@app.post("/register/complete")
async def register_complete(reg_data: RegistrationComplete):
    # Vérifier si l'inscription existe
    if reg_data.registration_id not in pending_registrations:
        raise HTTPException(status_code=400, detail="ID d'inscription invalide ou expiré")
    
    # Vérifier si le flow OAuth existe
    if reg_data.registration_id not in oauth_flows:
        raise HTTPException(status_code=400, detail="Session d'authentification expirée, veuillez recommencer")
    
    registration = pending_registrations[reg_data.registration_id]
    flow = oauth_flows[reg_data.registration_id]
    
    try:
        # Échanger le code d'autorisation contre des tokens
        flow.fetch_token(code=reg_data.auth_code)
        creds = flow.credentials
        
        # Sérialiser les credentials pour stockage (les credentials sont plus simples à sérialiser)
        token_pickle = pickle.dumps(creds)
        token_base64 = base64.b64encode(token_pickle).decode('utf-8')
        
        # Créer l'utilisateur avec son token Google
        user = UserCreate(
            username=registration["username"],
            email=registration["email"],
            password=registration["password"]
        )
        
        # Récupérer le hash du mot de passe
        hashed_password = get_password_hash(user.password)
        
        # Créer les paramètres par défaut
        default_settings = SMSNotificationSettings(
            agendaFields=['summary', 'date'],
            phoneNumber="+213123456789",
            keywords=[]
        )
        
        # Créer l'utilisateur dans la base de données
        user_dict = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "settings": default_settings.model_dump(),
            "google_token": token_base64
        }
        
        # Insérer l'utilisateur dans la base de données
        db.users.insert_one(user_dict)
        
        # Nettoyer les inscriptions et flux temporaires
        del pending_registrations[reg_data.registration_id]
        del oauth_flows[reg_data.registration_id]
        
        return {"message": "Utilisateur créé avec succès"}
        
    except Exception as e:
        # Nettoyer en cas d'erreur
        if reg_data.registration_id in pending_registrations:
            del pending_registrations[reg_data.registration_id]
        if reg_data.registration_id in oauth_flows:
            del oauth_flows[reg_data.registration_id]
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'authentification: {str(e)}")

@app.post("/login")
async def login(user: UserLogin):
    db_user = authenticate_user(user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Identifiants invalides")

    # Générer le token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )

    # Retourner le token au lieu du message "Connexion réussie"
    # return {"access_token": access_token, "token_type": "bearer"}
    # return(db_user)
    return {
        "username": db_user.username,
        "email": db_user.email,
        "settings": db_user.settings,  # Si `settings` existe dans ton modèle utilisateur
        "access_token": access_token,
        "token_type": "bearer",
    }


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
async def get_settings_for_user(username: str):
    settings = get_user_settings(username)
    if not settings:
        raise HTTPException(status_code=404, detail="Utilisateur ou paramètres non trouvés")
    return settings

@app.put("/update-settings")
async def update_settings(
    settings: SMSNotificationSettings,
    current_user: User = Depends(get_current_user)
):
    updated = update_user_settings(current_user.username, settings)
    if not updated:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Paramètres mis à jour avec succès"}

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

@app.post("/save-settings")
async def save_user_settings(
    agendaFields:List[str] , phoneNumber: str, current_user: User = Depends(get_current_user)
):
    user = get_user_by_username(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    settings = update_user_agenda_fields(current_user.username, agendaFields)
    if not settings:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    settings = update_user_phone_number(current_user.username, phoneNumber)
    if not settings:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return {"message": "Paramètres enregistrés avec succès"}