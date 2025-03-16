# def send_sms_raspisms(phone_number, message):
#     """
#     Sends an SMS via RaspiSMS API.
    
#     Args:
#         phone_number (str): The recipient's phone number
#         message (str): The message content to send
#     """
#     endpoint = f"{RASPISMS_URL}/api/scheduled/"
#     payload = {
#         "text": message,
#         "numbers": phone_number
#     }
#     headers = {
#         "X-Api-Key": API_KEY
#     }
#     try:
#         response = requests.post(endpoint, data=payload, headers=headers, verify=False)
#         if response.status_code in [200, 201]:
#             print(f"SMS sent successfully to {phone_number}")
#         else:
#             print(f"Error sending SMS: {response.status_code}")
#     except Exception as e:
#         print(f"Connection error to RaspiSMS: {str(e)}")

###############################################################################
# IoT SMS Notification System
# 
# This program monitors Google Calendar events and Google Classroom assignments
# for multiple users and sends SMS notifications based on user preferences.
# It uses MongoDB to store user data and RaspiSMS for sending SMS messages.
###############################################################################

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
import zoneinfo
import serial

###############################################################################
# Configuration and Connection Settings
###############################################################################

# Timezone Configuration for Algeria (UTC+1)
ALGERIA_TIMEZONE = zoneinfo.ZoneInfo("Africa/Algiers")

# MongoDB Connection
MONGO_URI = "mongodb+srv://lyouikene:youcef2003@cluster0.9ykf0.mongodb.net/?retryWrites=true&w=majority&appName=cluster0"
client = MongoClient(MONGO_URI)
db = client["iot_sms_notifications"]
users_collection = db["users"]

# RaspiSMS Configuration
API_KEY = "c48132fd786baa8fa9d42e01879ea166"
RASPISMS_URL = "http://192.168.161.237/raspisms"
RASPISMS_USER = "admin@example.com"
RASPISMS_PASSWORD = "Dq207Exhldb0CTC5bJg2joykTQVjkP52"

# Google API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly'
]

###############################################################################
# SMS Functionality
###############################################################################

ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)

def send_at_command(command, wait=3):
    """Envoie une commande AT et retourne la reponse."""
    ser.write((command + "\r\n").encode())  # Envoi de la commande
    time.sleep(wait)  # Attente de la reponse
    response = ser.read(ser.inWaiting()).decode(errors='ignore')  # Lecture de la reponse
    return response

def send_sms_raspisms(phone_number, message):
    """Envoie un SMS a un numero donne."""
    ser.write(('AT+CMGS="' + phone_number + '"\r\n').encode())  # Numero de destination
    time.sleep(1)
    ser.write((message + "\r\n").encode())  # Contenu du message
    time.sleep(1)
    ser.write(b"\x1A")  # Fin du message (CTRL+Z)
    time.sleep(3)
    print("SMS envoye !")

###############################################################################
# Authentication Functions
###############################################################################

def get_user_credentials(user):
    """
    Retrieves and deserializes Google API credentials from user data.
    
    Args:
        user (dict): User document from MongoDB
        
    Returns:
        object: Google API credentials object or None if error occurs
    """
    try:
        # Decode and deserialize the token
        token_base64 = user["google_token"]
        token_pickle = base64.b64decode(token_base64)
        credentials = pickle.loads(token_pickle)
        
        return credentials
    except Exception as e:
        print(f"Error retrieving credentials: {e}")
        return None

###############################################################################
# Google Calendar Functions
###############################################################################

def get_upcoming_events(creds):
    """
    Retrieves calendar events for the current day.
    
    Args:
        creds: Google API credentials
        
    Returns:
        list: List of calendar events
    """
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.now(ALGERIA_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
    
    # Convert to UTC for Google API
    start_of_day_utc = start_of_day.astimezone(UTC)
    end_of_day_utc = end_of_day.astimezone(UTC)
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_day_utc.isoformat(),
        timeMax=end_of_day_utc.isoformat(),
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def build_event_message(event, agenda_fields):
    """
    Builds a customized message for an event based on user-selected fields.
    
    Args:
        event (dict): Calendar event data
        agenda_fields (list): Fields to include in the message
        
    Returns:
        str: Formatted message containing selected event information
    """
    message_parts = []

    # Add each user-selected field to the message
    for field in agenda_fields:
        if field == "summary" and "summary" in event:
            message_parts.append(f"Titre : {event['summary']}")
        
        elif field == "start" and "start" in event:
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            if start_time:
                # Convert to Algeria timezone for display
                start_datetime = datetime.fromisoformat(start_time)
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.astimezone(ALGERIA_TIMEZONE)
                start_time_str = start_datetime.strftime("%d/%m/%Y %H:%M")
                message_parts.append(f"Debut : {start_time_str}")
        
        elif field == "end" and "end" in event:
            end_time = event["end"].get("dateTime", event["end"].get("date"))
            if end_time:
                # Convert to Algeria timezone for display
                end_datetime = datetime.fromisoformat(end_time)
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.astimezone(ALGERIA_TIMEZONE)
                end_time_str = end_datetime.strftime("%d/%m/%Y %H:%M")
                message_parts.append(f"Fin : {end_time_str}")
        
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

    # Join message parts with line breaks
    return "\n".join(message_parts)

###############################################################################
# Google Classroom Functions
###############################################################################

def get_classroom_courses(creds):
    """
    Retrieves Google Classroom courses.
    
    Args:
        creds: Google API credentials
        
    Returns:
        list: List of Classroom courses
    """
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().list(pageSize=100).execute()
    return results.get('courses', [])

def get_course_work(creds, course_id):
    """
    Retrieves coursework for a specific course.
    
    Args:
        creds: Google API credentials
        course_id (str): The course ID
        
    Returns:
        list: List of coursework items
    """
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().courseWork().list(courseId=course_id).execute()
    return results.get('courseWork', [])

def get_upcoming_assignments(creds, max_days_ahead=30):
    """
    Retrieves upcoming assignments due in the next days (max 30 days).
    
    Args:
        creds: Google API credentials
        max_days_ahead (int): Maximum number of days to look ahead
        
    Returns:
        list: List of upcoming assignments sorted by deadline
    """
    now = datetime.now(ALGERIA_TIMEZONE)  # Use Algeria timezone
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
                    
                    # Create deadline in UTC, then convert to Algeria timezone
                    deadline_utc = datetime(year, month, day, hour, minute, tzinfo=UTC)
                    deadline = deadline_utc.astimezone(ALGERIA_TIMEZONE)
                    
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

###############################################################################
# Notification Monitoring System
###############################################################################

# def check_events_and_assignments(user_id):
#     """
#     Main monitoring function that checks calendar events and classroom assignments.
#     Runs in a continuous loop for each user.
    
#     Args:
#         user_id (str): MongoDB ID of the user document
#     """
#     sent_notifications = set()
#     while True:
#         try:
#             user = users_collection.find_one({"_id": user_id})
#             if not user:
#                 print(f"User with ID {user_id} no longer exists. Stopping thread.")
#                 break

#             # Get user settings
#             username=user.get('username')
#             phone_number = user["settings"].get("phoneNumber", None)
#             agenda_fields = user["settings"].get("agendaFields", [])
#             keywords = [kw["text"] for kw in user["settings"].get("keywords", [])]
#             notification_times = {kw["text"]: kw.get("notificationTimes", []) for kw in user["settings"].get("keywords", [])}
#             creds=get_user_credentials(user)
#             print(f"---------------------------------------------------------")
#             print(f"\n {username} DATA:")
#             print(f" Phone Number: {phone_number}")
#             print(f"NOTIFICATION SETTINGS:")
#             print(f"Agenda Fields: {agenda_fields}")
#             for kw, times in notification_times.items():
#                 print(f"Keyword '{kw}' notification times: {times} minutes before")

#             now = datetime.now(ALGERIA_TIMEZONE)
#             events = get_upcoming_events(creds)

#             for event in events:
#                 try:
#                     event_id = event.get('id')
#                     event_summary = event.get("summary", "")

#                     # Find keyword that appears in the event title
#                     matched_keyword = next((kw for kw in keywords if kw in event_summary), None)
                    

                    
#                     # Check if we should send an SMS
#                     if not matched_keyword:
#                         continue

#                     # Get event start time and convert to Algeria timezone
#                     start_str = event['start'].get('dateTime', event['start'].get('date'))
#                     start_time_utc = datetime.fromisoformat(start_str)

                    

#                     if start_time_utc.tzinfo is not None:
#                         start_time = start_time_utc.astimezone(ALGERIA_TIMEZONE)
#                     else:
#                         # If no timezone info, assume it's in UTC
#                         start_time_utc = start_time_utc.replace(tzinfo=UTC)
#                         start_time = start_time_utc.astimezone(ALGERIA_TIMEZONE)
                    
#                     print("start time (Algeria) : ", start_time)
                    
#                     # Get notification times for this keyword
#                     notification_minutes = notification_times.get(matched_keyword, [])
#                     print(f"---------------------------------------------------------")
#                     print(f"\nFor user : {username}\nEvent : {event_summary}\nMatched word :  {matched_keyword}\nStart time : {start_time}\nNotification minutes : {notification_minutes}")
#                     print(f"---------------------------------------------------------")
                    
#                     if not notification_minutes:
#                         continue  # No notification times defined for this keyword

#                     for minutes_before in notification_minutes:
#                         notification_time = start_time - timedelta(minutes=minutes_before)
#                         notification_key = f"calendar_{event_id}_{notification_time.isoformat()}"
#                         # print("for user : ", user.get('username'), " with : ", phone_number)
#                         # print("notif time (Algeria) : ", notification_time)
#                         print(f"\nFor user : {username}\nEvent : {event_summary}\nNotification at : {notification_time}")

                        
#                         if notification_key not in sent_notifications:
#                             time_diff = abs((notification_time - now).total_seconds())
#                             print(f"Notification time : {notification_time}\nTime_diff : {time_diff}")

#                             if time_diff <= 300:  # 5-minute window
#                                 # Build SMS message dynamically
#                                 message = build_event_message(event, agenda_fields)
                                    
#                                 if not message:
#                                     continue  # No valid fields found
#                                 try:
#                                     send_sms_raspisms(phone_number, message)
#                                     sent_notifications.add(notification_key)
#                                     print(f"Notification sent for: {event_summary}")
#                                 except Exception as e:
#                                     print(f"Error sending SMS: {e}")
#                 except Exception as event_error:
#                     print(f"Error processing event: {event_error}")

#             assignments = get_upcoming_assignments(creds)
#             for assignment in assignments:
#                 try:
#                     assignment_title = assignment['title']
#                     assignment_deadline = assignment['deadline']
#                     classroom_course_name = assignment['course_name']
                    
#                     # Define notification times (1 day and 1 hour before)
#                     classroom_notification_minutes = [1440, 60]  # 1440 minutes = 24 hours, 60 minutes = 1 hour
                    
#                     for classroom_minutes_before in classroom_notification_minutes:
#                         classroom_notification_time = assignment_deadline - timedelta(minutes=classroom_minutes_before)
#                         classroom_notification_key = f"classroom_{assignment_title}_{classroom_notification_time.isoformat()}"
#                         # print("for classroom user: ", user.get('username'), " with: ", phone_number)
#                         # print("classroom notification time (Algeria): ", classroom_notification_time)
                        
#                         if classroom_notification_key not in sent_notifications:
#                             classroom_time_diff = abs((classroom_notification_time - now).total_seconds())
#                             # print("classroom_time_diff: ", classroom_time_diff)
                            
#                             if classroom_time_diff <= 300:  # 5-minute window
#                                 classroom_message = f"Classroom Deadline :\n'{assignment_title}' for {classroom_course_name} is due at {assignment_deadline.strftime('%H:%M')}"
#                                 try:
#                                     send_sms_raspisms(phone_number, classroom_message)
#                                     sent_notifications.add(classroom_notification_key)
#                                     print(f"Notification sent for classroom assignment: {assignment_title}")
#                                 except Exception as classroom_e:
#                                     print(f"Error sending classroom SMS: {classroom_e}")
                
#                 except Exception as classroom_assignment_error:
#                     print(f"Error processing classroom assignment: {classroom_assignment_error}")

#             # Clean up old notifications (older than 24 hours)
#             cutoff_time = now - timedelta(hours=24)
#             sent_notifications = {
#                 notif for notif in sent_notifications
#                 if datetime.fromisoformat(notif.split('_')[-1]) >= cutoff_time
#             }
#         except Exception as main_error:
#             print(f"Main error: {main_error}")
#         time.sleep(60)  # Check every minute

def check_events_and_assignments(user_id):
    """
    Main monitoring function that checks calendar events and classroom assignments.
    Runs in a continuous loop for each user.
    
    Args:
        user_id (str): MongoDB ID of the user document
    """
    sent_notifications = set()
    while True:
        try:
            user = users_collection.find_one({"_id": user_id})
            if not user:
                print(f"User with ID {user_id} no longer exists. Stopping thread.")
                break

            # Get user settings
            username=user.get('username')
            phone_number = user["settings"].get("phoneNumber", None)
            agenda_fields = user["settings"].get("agendaFields", [])
            keywords = [kw["text"] for kw in user["settings"].get("keywords", [])]
            notification_times = {kw["text"]: kw.get("notificationTimes", []) for kw in user["settings"].get("keywords", [])}
            creds=get_user_credentials(user)
            
            print("\n" + "="*50)
            print(f"USER: {username}")
            print(f"Phone: {phone_number}")
            print("-"*50)
            print(f"NOTIFICATION SETTINGS:")
            print(f"Agenda Fields: {', '.join(agenda_fields)}")
            for kw, times in notification_times.items():
                print(f"Keyword '{kw}' -> {', '.join(map(str, times))} minutes before")
            print("-"*50)

            now = datetime.now(ALGERIA_TIMEZONE)
            events = get_upcoming_events(creds)

            for event in events:
                try:
                    event_id = event.get('id')
                    event_summary = event.get("summary", "")

                    # Find keyword that appears in the event title
                    matched_keyword = next((kw for kw in keywords if kw in event_summary), None)
                    
                    # Check if we should send an SMS
                    if not matched_keyword:
                        continue

                    # Get event start time and convert to Algeria timezone
                    start_str = event['start'].get('dateTime', event['start'].get('date'))
                    start_time_utc = datetime.fromisoformat(start_str)

                    if start_time_utc.tzinfo is not None:
                        start_time = start_time_utc.astimezone(ALGERIA_TIMEZONE)
                    else:
                        # If no timezone info, assume it's in UTC
                        start_time_utc = start_time_utc.replace(tzinfo=UTC)
                        start_time = start_time_utc.astimezone(ALGERIA_TIMEZONE)
                    
                    # Get notification times for this keyword
                    notification_minutes = notification_times.get(matched_keyword, [])
                    print("\n" + "*"*25+ " <" + username + "> "+"*"*25)
                    print(f"EVENT MATCH: {event_summary}")
                    print(f"Matched keyword: {matched_keyword}")
                    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M')} (Algeria)")
                    print(f"Notifications: {', '.join(map(str, notification_minutes))} minutes before")
                    
                    if not notification_minutes:
                        continue  # No notification times defined for this keyword

                    for minutes_before in notification_minutes:
                        notification_time = start_time - timedelta(minutes=minutes_before)
                        notification_key = f"calendar_{event_id}_{notification_time.isoformat()}"
                    
                        if notification_key not in sent_notifications:
                            time_diff = abs((notification_time - now).total_seconds())
                            print(f"\nNOTIFICATION CHECK:")
                            print(f"User: {username}")
                            print(f"   Event: {event_summary}")
                            print(f"   Alert: {minutes_before} minutes before")
                            print(f"   Notify at: {notification_time.strftime('%Y-%m-%d %H:%M')}")
                            print(f"   Time difference: {time_diff:.1f} seconds")

                            if time_diff <= 300:  # 5-minute window
                                # Build SMS message dynamically
                                message = build_event_message(event, agenda_fields)
                                    
                                if not message:
                                    continue  # No valid fields found
                                try:
                                    send_sms_raspisms(phone_number, message)
                                    sent_notifications.add(notification_key)
                                    print(f"SMS SENT for: {event_summary}")
                                except Exception as e:
                                    print(f"SMS ERROR: {e}")
                except Exception as event_error:
                    print(f"EVENT PROCESSING ERROR: {event_error}")

            assignments = get_upcoming_assignments(creds)
            for assignment in assignments:
                try:
                    assignment_title = assignment['title']
                    assignment_deadline = assignment['deadline']
                    classroom_course_name = assignment['course_name']
                    
                    # Define notification times (1 day and 1 hour before)
                    classroom_notification_minutes = [1440, 60]  # 1440 minutes = 24 hours, 60 minutes = 1 hour
                    
                    print("\n" + "*"*25+ " <" + username + "> "+"*"*25)
                    print(f"CLASSROOM: {assignment_title}")
                    print(f"Course: {classroom_course_name}")
                    print(f"Deadline: {assignment_deadline.strftime('%Y-%m-%d %H:%M')}")
                    
                    for classroom_minutes_before in classroom_notification_minutes:
                        classroom_notification_time = assignment_deadline - timedelta(minutes=classroom_minutes_before)
                        classroom_notification_key = f"classroom_{assignment_title}_{classroom_notification_time.isoformat()}"
                        
                        
                        
                        if classroom_notification_key not in sent_notifications:
                            classroom_time_diff = abs((classroom_notification_time - now).total_seconds())
                            print(f"\nCLASSROOM NOTIFICATION:")
                            print(f"   Alert: {classroom_minutes_before} minutes before")
                            print(f"   Notify at: {classroom_notification_time.strftime('%Y-%m-%d %H:%M')}")   
                            print(f"   Time difference: {classroom_time_diff:.1f} seconds")
                            
                            if classroom_time_diff <= 300:  # 5-minute window
                                classroom_message = f"Classroom Deadline :\n'{assignment_title}' for {classroom_course_name} is due at {assignment_deadline.strftime('%H:%M')}"
                                try:
                                    send_sms_raspisms(phone_number, classroom_message)
                                    sent_notifications.add(classroom_notification_key)
                                    print(f"CLASSROOM SMS SENT for: {assignment_title}")
                                except Exception as classroom_e:
                                    print(f"CLASSROOM SMS ERROR: {classroom_e}")
                
                except Exception as classroom_assignment_error:
                    print(f"CLASSROOM PROCESSING ERROR: {classroom_assignment_error}")

             # Clean up old notifications (older than 24 hours)
            cutoff_time = now - timedelta(hours=24)
            sent_notifications = {
                notif for notif in sent_notifications
                if datetime.fromisoformat(notif.split('_')[-1]) >= cutoff_time
            }
        except Exception as main_error:
            print(f"MAIN ERROR: {main_error}")
        
        print("\n" + "="*50)
        print(f"Sleeping for 60 seconds...")
        print("="*50)
        time.sleep(60)  # Check every minute

###############################################################################
# User Thread Management
###############################################################################

def start_user_thread(user):
    """
    Starts a monitoring thread for a user.
    
    Args:
        user (dict): User document from MongoDB
    """
    email = user.get("email")
    if not email:
        print(f"Missing email address for user: {user.get('username')}")
        return

    try:
        print(f"Starting thread for user: {email}")
        thread = threading.Thread(
            target=check_events_and_assignments,
            args=(user["_id"],),
            daemon=True
        )
        thread.start()
    except Exception as e:
        print(f"Unable to load credentials for user: {email}, error: {e}")

def watch_users_collection(users_collection):
    """
    Monitors the users collection for new users.
    
    Args:
        users_collection: MongoDB collection object
    """
    print("Monitoring for new users...")
    with users_collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
        for change in stream:
            new_user = change["fullDocument"]
            print(f"New user detected: {new_user.get('email')}")
            start_user_thread(new_user)

###############################################################################
# Main Function
###############################################################################

def main():
    """
    Main function to monitor new users and start threads.
    """
    print(f"Starting IoT SMS Notification System with Algeria timezone (UTC+1)")
    
    # Start threads for existing users
    users = users_collection.find()
    for user in users:
        start_user_thread(user)

    # Monitor for new users
    watch_users_collection(users_collection)
    ser.close()

if __name__ == '__main__':
    main()  
