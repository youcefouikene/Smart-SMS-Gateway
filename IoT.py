import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta, UTC
import pickle
import os
import time
import threading
import requests
from pymongo import MongoClient

# Connexion a MongoDB
MONGO_URI = "mongodb+srv://lyouikene:youcef2003@cluster0.9ykf0.mongodb.net/?retryWrites=true&w=majority&appName=cluster0"
client = MongoClient(MONGO_URI)
db = client["iot_sms_notifications"]
users_collection = db["users"]

# Configuration RaspiSMS
API_KEY = "c48132fd786baa8fa9d42e01879ea166"
RASPISMS_URL = "http://192.168.100.55/raspisms"
RASPISMS_USER = "admin@example.com"
RASPISMS_PASSWORD = "Dq207Exhldb0CTC5bJg2joykTQVjkP52"

# Scopes pour Google Calendar et Classroom
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly'
]

def send_sms_raspisms(phone_number, message):
    """Envoie un SMS via RaspiSMS."""
    endpoint = f"{RASPISMS_URL}/api/scheduled/"
    payload = {
        "text": message,
        "numbers": phone_number
    }
    headers = {
        "X-Api-Key": API_KEY
    }
    try:
        response = requests.post(endpoint, data=payload, headers=headers, verify=False)
        if response.status_code in [200, 201]:
            print(f"SMS envoye avec succes a {phone_number}")
        else:
            print(f"Erreur lors de l'envoi du SMS: {response.status_code}")
    except Exception as e:
        print(f"Erreur de connexion a RaspiSMS: {str(e)}")

def authenticate_email(email):
    """Authentifie l'utilisateur avec une nouvelle adresse e-mail via OAuth 2.0."""
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    print(f"Veuillez vous connecter avec l'adresse e-mail : {email}")
    print(f"Ouvrez ce lien dans votre navigateur : {auth_url}")
    code = input("Entrez le code d'autorisation : ")
    flow.fetch_token(code=code)
    creds = flow.credentials
    with open(f'token_{email}.json', 'wb') as token:
        pickle.dump(creds, token)
    return creds

def load_credentials(email):
    """Charge les informations d'authentification pour une adresse e-mail."""
    token_file = f'token_{email}.json'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
            return creds
    return None

def get_user_credentials(user):
    try:
        # Décoder et désérialiser le token
        token_base64 = user["google_token"]
        token_pickle = base64.b64decode(token_base64)
        credentials = pickle.loads(token_pickle)
        
        return credentials
    except Exception as e:
        print(f"Erreur lors de la récupération des credentials: {e}")
        return None

def get_upcoming_events(creds):
    """Recupere les evenements de la journee en cours."""
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.now(UTC)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def get_classroom_courses(creds):
    """Recupere la liste des cours Google Classroom."""
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().list(pageSize=100).execute()
    return results.get('courses', [])

def get_course_work(creds, course_id):
    """Recupere les devoirs pour un cours specifique."""
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().courseWork().list(courseId=course_id).execute()
    return results.get('courseWork', [])

def get_upcoming_assignments(creds, max_days_ahead=30):
    """Recupere les devoirs a venir dans les prochains jours (max 30 jours)."""
    now = datetime.now(UTC)
    max_date = now + timedelta(days=max_days_ahead)
    upcoming_assignments = []
    courses = get_classroom_courses(creds)
    for course in courses:
        if course.get('courseState') == 'ACTIVE':
            course_id = course['id']
            course_name = course['name']
            assignments = get_course_work(creds, course_id)
            for assignment in assignments:
                if 'dueDate' in assignment:
                    due_date = assignment.get('dueDate', {})
                    due_time = assignment.get('dueTime', {'hours': 23, 'minutes': 59})
                    year = due_date.get('year', 1970)
                    month = due_date.get('month', 1)
                    day = due_date.get('day', 1)
                    hour = due_time.get('hours', 23)
                    minute = due_time.get('minutes', 59)
                    deadline = datetime(year, month, day, hour, minute, tzinfo=UTC)
                    if now <= deadline <= max_date:
                        upcoming_assignments.append({
                            'title': assignment['title'],
                            'course_name': course_name,
                            'deadline': deadline,
                            'description': assignment.get('description', ''),
                            'link': assignment.get('alternateLink', '')
                        })
    upcoming_assignments.sort(key=lambda x: x['deadline'])
    return upcoming_assignments

def build_event_message(event, agenda_fields):
    """
    Construit un message personnalisé pour un événement en fonction des champs choisis par l'utilisateur.
    """
    message_parts = []

    # Ajouter chaque champ choisi par l'utilisateur au message
    for field in agenda_fields:
        if field == "summary" and "summary" in event:
            message_parts.append(f"Titre : {event['summary']}")
        
        elif field == "start" and "start" in event:
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            if start_time:
                start_time = datetime.fromisoformat(start_time).strftime("%d/%m/%Y %H:%M")
                message_parts.append(f"Début : {start_time}")
        
        elif field == "end" and "end" in event:
            end_time = event["end"].get("dateTime", event["end"].get("date"))
            if end_time:
                end_time = datetime.fromisoformat(end_time).strftime("%d/%m/%Y %H:%M")
                message_parts.append(f"Fin : {end_time}")
        
        elif field == "location" and "location" in event:
            message_parts.append(f"Lieu : {event['location']}")
        
        elif field == "description" and "description" in event:
            message_parts.append(f"Description : {event['description']}")
        
        elif field == "organizer" and "organizer" in event:
            organizer_email = event["organizer"].get("email", "")
            organizer_name = event["organizer"].get("displayName", "")
            if organizer_name:
                message_parts.append(f"Organisateur : {organizer_name} ({organizer_email})")
            else:
                message_parts.append(f"Organisateur : {organizer_email}")

    # Joindre les parties du message avec des sauts de ligne
    return "\n".join(message_parts)

def check_events_and_assignments(user):
    """Verifie les evenements du calendrier et les devoirs Classroom."""
    sent_notifications = set()
    while True:
        try:
            now = datetime.now(UTC)
            events = get_upcoming_events(get_user_credentials(user))
            print("done with events")
            for event in events:
                try:
                    event_id = event.get('id')
                    event_summary = event.get("summary", "")

                    print("event summary : ",event_summary)

                    # Recuperer les settings de l'utilisateur
                    phone_number = user["settings"].get("phoneNumber", None)
                    agenda_fields = user["settings"].get("agendaFields", [])
                    keywords = [kw["text"] for kw in user["settings"].get("keywords", [])]
                    notification_times = {kw["text"]: kw.get("notificationTimes", []) for kw in user["settings"].get("keywords", [])}

                    print(notification_times)

                    # Recuperer le mot cle qui apparait dans le titre du event
                    matched_keyword = next((kw for kw in keywords if kw in event_summary), None)

                    print("matched word : ",matched_keyword)
                    
                    # Verifier si nous devons envoyer un SMS ou pas
                    if not matched_keyword :
                        continue

                    # Recuperer la date debut de l'event
                    start_str = event['start'].get('dateTime', event['start'].get('date'))
                    start_time = datetime.fromisoformat(start_str)
                    
                    print("start time : ",start_time)
                    
                    
                    # Recuperer les moments de notifications pour ce mot-cle
                    notification_minutes = notification_times.get(matched_keyword, [])
                    
                    if not notification_minutes:
                        continue  # Aucun moment de notification defini pour ce mot-cle

                    for minutes_before in notification_minutes:
                        notification_time = start_time - timedelta(minutes=minutes_before)
                        notification_key = f"calendar_{event_id}_{notification_time.isoformat()}"
                        print("for user : ",user.get('username')," with : ",phone_number)
                        print("notif time : ",notification_time)
                        

                        if notification_key not in sent_notifications:
                            time_diff = abs((notification_time - now).total_seconds())
                            print("time_diff : ",time_diff)
                            if time_diff <= 300:  # Fenêtre de 5 minutes
                                # Construire le message SMS dynamiquement
                                message = build_event_message(event , agenda_fields)
                                    
                                if not message:
                                    continue  # Aucun champ valide trouvé
                                try:
                                    send_sms_raspisms(phone_number, message)
                                    sent_notifications.add(notification_key)
                                    print(f"Notification envoyee pour: {event_summary}")
                                except Exception as e:
                                    print(f"Erreur lors de l'envoi du SMS: {e}")
                except Exception as event_error:
                    print(f"Erreur lors du traitement de l'evenement: {event_error}")

            cutoff_time = now - timedelta(hours=24)
            sent_notifications = {
                notif for notif in sent_notifications
                if datetime.fromisoformat(notif.split('_')[-1]) >= cutoff_time
            }
        except Exception as main_error:
            print(f"Erreur principale: {main_error}")
        time.sleep(60)

def start_user_thread(user):
    """Demarre un thread pour un utilisateur."""
    email = user.get("email")
    if not email:
        print(f"Adresse e-mail manquante pour l'utilisateur : {user.get('username')}")
        return

    # Charger les credentials de l'utilisateur
    # creds = load_credentials(email)
    # if not creds:
    #     print(f"Authentification necessaire pour l'utilisateur : {email}")
    #     creds = authenticate_email(email)

    # if creds:
    try :
        print(f"Lancement du thread pour l'utilisateur : {email}")
        thread = threading.Thread(
            target=check_events_and_assignments,
            args=(user),
            daemon=True
        )
        thread.start()
    except Exception  :
        print(f"Impossible de charger les credentials pour l'utilisateur : {email}")

def watch_users_collection(users_collection):
    """Surveille la collection users pour detecter les nouveaux utilisateurs."""
    print("Surveillance des nouveaux utilisateurs...")
    with users_collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
        for change in stream:
            new_user = change["fullDocument"]
            print(f"Nouvel utilisateur detecte : {new_user.get('email')}")
            start_user_thread(new_user)

def main():
    """Fonction principale pour surveiller les nouveaux utilisateurs et lancer des threads."""

    # Demarrer les threads pour les utilisateurs existants
    users = users_collection.find()
    for user in users:
        start_user_thread(user)

    # Surveiller les nouveaux utilisateurs
    watch_users_collection(users_collection)

if __name__ == '__main__':
    main()
