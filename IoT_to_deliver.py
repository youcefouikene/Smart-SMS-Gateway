###############################################################################
# IoT SMS Notification System
# 
# This program monitors Google Calendar events and Google Classroom assignments
# for multiple users and sends SMS notifications based on user preferences.
# It uses MongoDB to store user data and RaspiSMS for sending SMS messages.
#
# The system is designed to run in an Algerian timezone context (UTC+1) and
# provides customizable notifications for educational purposes.
###############################################################################

# Import necessary libraries
import base64                                     # For encoding/decoding credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # For Google OAuth authentication
from google.auth.transport.requests import Request      # For refreshing Google API tokens
from googleapiclient.discovery import build             # For building Google API service objects
from datetime import datetime, timedelta, UTC           # For date/time handling
import pickle                                     # For serializing/deserializing credentials
import os                                         # For file operations
import time                                       # For time-related operations
import threading                                  # For concurrent execution
import requests                                   # For HTTP requests to RaspiSMS API
from pymongo import MongoClient                   # For MongoDB database connections
import zoneinfo                                   # For timezone handling
import serial                                     # For serial communication (potentially with SMS hardware)
import json
import requets
from azure.iot.device import IoTHubModuleClient

###############################################################################
# Configuration and Connection Settings
###############################################################################

# Define Algeria timezone (UTC+1) for consistent date/time handling across the application
ALGERIA_TIMEZONE = zoneinfo.ZoneInfo("Africa/Algiers")

# MongoDB connection string and database initialization
# This database stores user preferences, tokens, and notification settings
MONGO_URI = "mongodb+srv://lyouikene:youcef2003@cluster0.9ykf0.mongodb.net/?retryWrites=true&w=majority&appName=cluster0"
client = MongoClient(MONGO_URI)
db = client["iot_sms_notifications"]
users_collection = db["users"]

# RaspiSMS API configuration
# RaspiSMS is used as the SMS gateway service for sending notifications
API_KEY = "c48132fd786baa8fa9d42e01879ea166"
RASPISMS_URL = "http://192.168.161.237/raspisms"
RASPISMS_USER = "admin@example.com"
RASPISMS_PASSWORD = "b4MT6hAnyc6nN03wiUdbJhxh42SzZ761"

# Google API scopes required for accessing calendar and classroom data
# These permissions will be requested during OAuth authentication
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',        # Read-only access to Google Calendar
    'https://www.googleapis.com/auth/classroom.courses.readonly',  # Read-only access to course listings
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',      # Read-only access to user's submissions
    'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly' # Read-only access to student submissions
]

# Global variables for synchronization and events caching (IoT Edge)
cached_events = []         # List of events synchronized from Google Calendar
cached_assignments = []    # List of assignments synchronized from Google Classroom
current_sync_token = None  # Token used to retrieve only modifications
edge_events = []           # Local cache simulating events stored on IoT Edge
edge_assignments = []      # Local cache simulating assignments stored on IoT Edge
notified_event_ids = set() # To avoid sending multiple SMS for the same event
notified_assignment_ids = set() # To avoid sending multiple SMS for the same assignment

###############################################################################
# SMS Functionality
###############################################################################

def send_sms_raspisms(phone_number, message):
    """
    Sends an SMS via RaspiSMS API.
    
    This function constructs the API request with proper headers and payload,
    then sends it to the RaspiSMS server. It handles basic error logging.
    
    Args:
        phone_number (str): The recipient's phone number
        message (str): The message content to send
    """
    # Construct the API endpoint URL for scheduled messages
    endpoint = f"{RASPISMS_URL}/api/scheduled/"
    
    # Prepare the request payload with message text and recipient number
    payload = {
        "text": message,
        "numbers": phone_number
    }
    
    # Set up authentication headers with the API key
    headers = {
        "X-Api-Key": API_KEY
    }
    
    # Attempt to send the SMS and handle any exceptions
    try:
        # Send POST request to the RaspiSMS API
        response = requests.post(endpoint, data=payload, headers=headers, verify=False)
        
        # Check if the request was successful (HTTP 200 or 201)
        if response.status_code in [200, 201]:
            print(f"SMS sent successfully to {phone_number}")
        else:
            # Log error if the request was unsuccessful
            print(f"Error sending SMS: {response.status_code}")
    except Exception as e:
        # Handle connection errors or other exceptions
        print(f"Connection error to RaspiSMS: {str(e)}")

###############################################################################
# Authentication Functions
###############################################################################

def get_user_credentials(user):
    """
    Retrieves and deserializes Google API credentials from user data.
    
    This function extracts the base64-encoded credential token from the user document,
    decodes it, and deserializes it into a usable credentials object.
    
    Args:
        user (dict): User document from MongoDB
        
    Returns:
        object: Google API credentials object to access Google APIs or None if error occurs
    """
    try:
        # Extract the base64-encoded token from the user document
        token_base64 = user["google_token"]
        
        # Decode the base64 string to binary data
        token_pickle = base64.b64decode(token_base64)
        
        # Deserialize the binary data into a credentials object
        credentials = pickle.loads(token_pickle)
        
        return credentials
    except Exception as e:
        # Handle any errors in the retrieval process
        print(f"Error retrieving credentials: {e}")
        return None

###############################################################################
# Google Calendar Functions
###############################################################################

def get_upcoming_events(creds):
    """
    Retrieves calendar events for the current day.
    
    This function connects to the Google Calendar API, calculates the time range
    for the current day in Algeria timezone, and fetches events within that range.
    
    Args:
        creds: Google API credentials
        
    Returns:
        list: List of calendar events
    """
    # Build the Calendar API service object using the provided credentials
    service = build('calendar', 'v3', credentials=creds)
    
    # Get current time in Algeria timezone
    now = datetime.now(ALGERIA_TIMEZONE)
    
    # Calculate start of day (midnight) in Algeria timezone
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate end of day (23:59:59) in Algeria timezone
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
    
    # Convert both timestamps to UTC for the Google API
    # (Google Calendar API requires UTC timestamps)
    start_of_day_utc = start_of_day.astimezone(UTC)
    end_of_day_utc = end_of_day.astimezone(UTC)
    
    # Fetch events from the primary calendar within the specified time range
    events_result = service.events().list(
        calendarId='primary',                      # Use the user's primary calendar
        timeMin=start_of_day_utc.isoformat(),      # Start time in ISO format
        timeMax=end_of_day_utc.isoformat(),        # End time in ISO format
        maxResults=10,                            # Limit to 10 events for efficiency
        singleEvents=True,                        # Expand recurring events
        orderBy='startTime'                       # Sort by start time
    ).execute()
    
    # Extract and return the list of events from the response
    return events_result.get('items', [])

def build_event_message(event, agenda_fields):
    """
    Builds a customized message for an event based on user-selected fields.
    
    This function constructs an SMS message containing only the fields that
    the user has specified in their preferences.
    
    Args:
        event (dict): Calendar event data
        agenda_fields (list): Fields to include in the message
        
    Returns:
        str: Formatted message containing selected event information
    """
    # Initialize an empty list to store message components
    message_parts = []

    # Add each user-selected field to the message
    for field in agenda_fields:
        # Include the event title/summary if selected
        if field == "summary" and "summary" in event:
            message_parts.append(f"Title: {event['summary']}")
        
        # Include the start time if selected
        elif field == "start" and "start" in event:
            # Get the start time (either dateTime for specific times or date for all-day events)
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            if start_time:
                # Convert to Algeria timezone for display
                start_datetime = datetime.fromisoformat(start_time)
                # Only convert if the datetime has timezone info
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.astimezone(ALGERIA_TIMEZONE)
                # Format the date and time in a user-friendly format
                start_time_str = start_datetime.strftime("%d/%m/%Y %H:%M")
                message_parts.append(f"Start: {start_time_str}")
        
        # Include the end time if selected
        elif field == "end" and "end" in event:
            # Get the end time (either dateTime for specific times or date for all-day events)
            end_time = event["end"].get("dateTime", event["end"].get("date"))
            if end_time:
                # Convert to Algeria timezone for display
                end_datetime = datetime.fromisoformat(end_time)
                # Only convert if the datetime has timezone info
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.astimezone(ALGERIA_TIMEZONE)
                # Format the date and time in a user-friendly format
                end_time_str = end_datetime.strftime("%d/%m/%Y %H:%M")
                message_parts.append(f"End: {end_time_str}")
        
        # Include the location if selected
        elif field == "location" and "location" in event:
            message_parts.append(f"Location: {event['location']}")
        
        # Include the description if selected
        elif field == "description" and "description" in event:
            message_parts.append(f"Description: {event['description']}")
        
        # Include the organizer information if selected
        elif field == "organizer" and "organizer" in event:
            # Extract organizer details
            organizer_email = event["organizer"].get("email", "")
            organizer_name = event["organizer"].get("displayName", "")
            # Format differently based on whether a display name is available
            if organizer_name:
                message_parts.append(f"Organizer: {organizer_name} ({organizer_email})")
            else:
                message_parts.append(f"Organizer: {organizer_email}")

    # Join all message parts with line breaks to create the final message
    return "\n".join(message_parts)

###############################################################################
# Google Classroom Functions
###############################################################################

def get_classroom_courses(creds):
    """
    Retrieves Google Classroom courses.
    
    This function connects to the Google Classroom API and fetches
    all courses that the user is enrolled in.
    
    Args:
        creds: Google API credentials
        
    Returns:
        list: List of Classroom courses
    """
    # Build the Classroom API service object using the provided credentials
    service = build('classroom', 'v1', credentials=creds)
    
    # Fetch up to 100 courses (pagination could be implemented for more)
    results = service.courses().list(pageSize=100).execute()
    
    # Extract and return the list of courses from the response
    return results.get('courses', [])

def get_course_work(creds, course_id):
    """
    Retrieves coursework for a specific course.
    
    This function connects to the Google Classroom API and fetches
    all coursework items for the specified course.
    
    Args:
        creds: Google API credentials
        course_id (str): The course ID
        
    Returns:
        list: List of coursework items
    """
    # Build the Classroom API service object using the provided credentials
    service = build('classroom', 'v1', credentials=creds)
    
    # Fetch coursework for the specified course
    results = service.courses().courseWork().list(courseId=course_id).execute()
    
    # Extract and return the list of coursework items from the response
    return results.get('courseWork', [])

def get_upcoming_assignments(creds, max_days_ahead=30):
    """
    Retrieves upcoming assignments due in the next days (max 30 days).
    
    This function fetches all active courses, then retrieves assignments for each
    course, filtering for those due within the specified time window and sorting
    them by deadline.
    
    Args:
        creds: Google API credentials
        max_days_ahead (int): Maximum number of days to look ahead
        
    Returns:
        list: List of upcoming assignments sorted by deadline
    """
    # Get current time in Algeria timezone
    now = datetime.now(ALGERIA_TIMEZONE)
    
    # Calculate the maximum future date to consider
    max_date = now + timedelta(days=max_days_ahead)
    
    # Initialize empty list to store upcoming assignments
    upcoming_assignments = []
    
    # Fetch all courses the user is enrolled in
    courses = get_classroom_courses(creds)
    
    # Process each active course
    for course in courses:
        # Only consider active courses (ignore archived or completed ones)
        if course.get('courseState') == 'ACTIVE':
            # Extract course ID and name
            course_id = course['id']
            course_name = course['name']
            
            # Fetch all coursework for this course
            assignments = get_course_work(creds, course_id)
            
            # Process each assignment
            for assignment in assignments:
                # Only consider assignments with due dates
                if 'dueDate' in assignment:
                    # Extract due date components
                    due_date = assignment.get('dueDate', {})
                    # Extract due time (default to end of day if not specified)
                    due_time = assignment.get('dueTime', {'hours': 23, 'minutes': 59})
                    
                    # Extract individual date components with default values
                    year = due_date.get('year', 1970)
                    month = due_date.get('month', 1)
                    day = due_date.get('day', 1)
                    hour = due_time.get('hours', 23)
                    minute = due_time.get('minutes', 59)
                    
                    # Create deadline datetime in UTC
                    deadline_utc = datetime(year, month, day, hour, minute, tzinfo=UTC)
                    
                    # Convert deadline to Algeria timezone for comparison and display
                    deadline = deadline_utc.astimezone(ALGERIA_TIMEZONE)
                    
                    # Check if the assignment is due within our time window
                    if now <= deadline <= max_date:
                        # Add assignment to our list with relevant details
                        upcoming_assignments.append({
                            'title': assignment['title'],
                            'course_name': course_name,
                            'deadline': deadline,
                            'description': assignment.get('description', ''),
                            'link': assignment.get('alternateLink', '')
                        })
    
    # Sort assignments by deadline (earliest first)
    upcoming_assignments.sort(key=lambda x: x['deadline'])
    return upcoming_assignments

###############################################################################
# IoT Edge Functions
###############################################################################

def calendar_sync_thread(creds):
    """
    Thread for synchronization with Google Calendar.
    
    - First performs a complete synchronization (full sync) if no sync token exists.
    - Then, in a loop, uses the sync token to retrieve only modifications.
    - In case of changes, updates the local cache and sends events to IoT Edge.
    """
    global current_sync_token, cached_events, cached_assignments

    # Initial complete synchronization
    if current_sync_token is None:
        events, new_token = get_calendar_events_sync(creds, None)
        cached_events = events
        current_sync_token = new_token
        
        # Retrieve Classroom assignments
        cached_assignments = get_upcoming_assignments(creds)
        
        # Send both types of data to IoT Edge
        send_to_iot_edge(cached_events, cached_assignments)
    
    # Incremental synchronization
    while True:
        # Synchronize with Calendar
        changes, new_token = get_calendar_events_sync(creds, current_sync_token)
        calendar_updated = False
        
        if changes:
            cached_events = update_cached_events(changes, cached_events)
            current_sync_token = new_token
            calendar_updated = True
            print("Changes detected in Google Calendar.")
        else:
            print("No changes detected in Google Calendar.")
        
        # Synchronize with Classroom (no sync token, so complete sync)
        new_assignments = get_upcoming_assignments(creds)
        classroom_updated = False
        
        # Check if there are changes in assignments
        if json.dumps(sorted(new_assignments, key=lambda x: x['id'])) != json.dumps(sorted(cached_assignments, key=lambda x: x['id'])):
            cached_assignments = new_assignments
            classroom_updated = True
            print("Changes detected in Google Classroom.")
        else:
            print("No changes detected in Google Classroom.")
            
        # Send to IoT Edge if something has changed
        if calendar_updated or classroom_updated:
            send_to_iot_edge(cached_events, cached_assignments)
        
        time.sleep(60)  # Check every 60 seconds

def send_to_iot_edge(events, assignments):
    """
    Sends events and assignments to Azure IoT Edge via Azure IoT Hub.
    Also updates the local cache simulating elements on the edge.
    """
    global edge_events, edge_assignments
    try:
        client = IoTHubModuleClient.create_from_connection_string(IOT_HUB_CONNECTION_STRING)
        MAX_ITEMS = 50  # Adjust according to your needs
        
        # Send Calendar events
        message_events = json.dumps({"events": events[:MAX_ITEMS]})
        client.send_message(message_events)
        print("Calendar events sent to IoT Edge.")
        
        # Send Classroom assignments
        message_assignments = json.dumps({"assignments": assignments[:MAX_ITEMS]})
        client.send_message(message_assignments)
        print("Classroom assignments sent to IoT Edge.")
    except Exception as e:
        print(f"Error when sending to IoT Edge: {e}")
    finally:
        client.shutdown()
    
    # Update local caches
    edge_events = events
    edge_assignments = assignments

def get_events_from_edge():
    """
    Returns events stored in the local cache simulating Azure IoT Edge.
    """
    return edge_events

def get_assignments_from_edge():
    """
    Returns assignments stored in the local cache simulating Azure IoT Edge.
    """
    return edge_assignments

def get_calendar_events_sync(creds, sync_token):
    """
    Retrieves events from Google Calendar.
    
    If sync_token is None, performs a complete synchronization (full sync).
    Otherwise, retrieves only modifications since the last sync token.
    
    Returns a tuple (list_of_events, new_sync_token).
    """
    service = build('calendar', 'v3', credentials=creds)
    
    if sync_token is None:
        # Complete synchronization
        print("Complete synchronization with Google Calendar...")
        request = service.events().list(
            calendarId='primary',
            showDeleted=True,
            singleEvents=True,
            orderBy='startTime'
        )
        all_events = []
        response = request.execute()
        all_events.extend(response.get('items', []))
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.events().list(
                calendarId='primary',
                showDeleted=True,
                singleEvents=True,
                orderBy='startTime',
                pageToken=page_token
            ).execute()
            all_events.extend(response.get('items', []))
        new_sync_token = response.get('nextSyncToken')
        return all_events, new_sync_token
    else:
        try:
            # Incremental retrieval: only modifications
            print("Checking for modifications via sync token...")
            response = service.events().list(
                calendarId='primary',
                syncToken=sync_token,
                showDeleted=True
            ).execute()
            changes = response.get('items', [])
            new_sync_token = response.get('nextSyncToken')
            return changes, new_sync_token
        except Exception as e:
            # In case of error (expired/invalid sync token), restart complete synchronization
            print("Invalid or expired sync token, restarting complete synchronization.")
            request = service.events().list(
                calendarId='primary',
                showDeleted=True,
                singleEvents=True,
                orderBy='startTime'
            )
            all_events = []
            response = request.execute()
            all_events.extend(response.get('items', []))
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.events().list(
                    calendarId='primary',
                    showDeleted=True,
                    singleEvents=True,
                    orderBy='startTime',
                    pageToken=page_token
                ).execute()
                all_events.extend(response.get('items', []))
            new_sync_token = response.get('nextSyncToken')
            
            return all_events, new_sync_token

def update_cached_events(changes, current_events):
    """
    Updates the current list of events by applying modifications.
    
    - If an event is canceled (status == 'cancelled'), it is removed.
    - Otherwise, the event is added or updated.
    """
    events_dict = {event['id']: event for event in current_events if 'id' in event}
    for change in changes:
        event_id = change.get('id')
        if not event_id:
            continue
        if change.get('status') == 'cancelled':
            if event_id in events_dict:
                del events_dict[event_id]
        else:
            events_dict[event_id] = change
    return list(events_dict.values())

###############################################################################
# Notification Monitoring System
###############################################################################

def check_events_and_assignments(user_id):
    """
    Main monitoring function that checks calendar events and classroom assignments.
    Runs in a continuous loop for each user.
    
    Args:
        user_id (str): MongoDB ID of the user document
    """
    # Initialize a set to track notifications that have already been sent
    # This prevents duplicate notifications for the same event
    sent_notifications = set()
    
    # Continuous monitoring loop
    while True:
        try:
            # Fetch the current user information from MongoDB
            user = users_collection.find_one({"_id": user_id})
            
            # Check if user still exists (they might have been deleted)
            if not user:
                print(f"User with ID {user_id} no longer exists. Stopping thread.")
                break

            # Extract user settings and preferences from the MongoDB document
            username = user.get('username')
            phone_number = user["settings"].get("phoneNumber", None)
            agenda_fields = user["settings"].get("agendaFields", [])
            
            # Extract keywords that trigger notifications
            keywords = [kw["text"] for kw in user["settings"].get("keywords", [])]
            
            # Create a dictionary mapping keywords to their notification times
            notification_times = {kw["text"]: kw.get("notificationTimes", []) 
                                 for kw in user["settings"].get("keywords", [])}
            
            # Get Google API credentials for this user
            creds = get_user_credentials(user)
            
            # Print user information and notification settings
            print("\n" + "="*50)
            print(f"USER: {username}")
            print(f"Phone: {phone_number}")
            print("-"*50)
            print(f"NOTIFICATION SETTINGS:")
            print(f"Agenda Fields: {', '.join(agenda_fields)}")
            for kw, times in notification_times.items():
                print(f"Keyword '{kw}' -> {', '.join(map(str, times))} minutes before")
            print("-"*50)

            # Get current time in Algeria timezone
            now = datetime.now(ALGERIA_TIMEZONE)

            # ------------- CALENDAR EVENTS PROCESSING -------------
            
            # Get user's events for the current day
            events = get_upcoming_events(creds)

            # Process each calendar event
            for event in events:
                try:
                    # Extract event ID and summary (title)
                    event_id = event.get('id')
                    event_summary = event.get("summary", "")

                    # Find the first keyword that appears in the event title
                    # Returns None if no keyword matches
                    matched_keyword = next((kw for kw in keywords if kw in event_summary), None)
                    
                    # Skip if no keyword matches this event
                    if not matched_keyword:
                        continue

                    # Get event start time from the event data
                    start_str = event['start'].get('dateTime', event['start'].get('date'))
                    start_time_utc = datetime.fromisoformat(start_str)

                    # Convert to Algeria timezone for consistent processing
                    if start_time_utc.tzinfo is not None:
                        # If the datetime already has timezone info
                        start_time = start_time_utc.astimezone(ALGERIA_TIMEZONE)
                    else:
                        # If no timezone info, assume it's in UTC
                        start_time_utc = start_time_utc.replace(tzinfo=UTC)
                        start_time = start_time_utc.astimezone(ALGERIA_TIMEZONE)
                    
                    # Get notification times for the matched keyword
                    notification_minutes = notification_times.get(matched_keyword, [])
                    
                    # Log event match details
                    print("\n" + "*"*25 + username + "*"*25)
                    print(f"EVENT MATCH: {event_summary}")
                    print(f"Matched keyword: {matched_keyword}")
                    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M')} (Algeria)")
                    print(f"Notifications: {', '.join(map(str, notification_minutes))} minutes before")
                    
                    # Skip if no notification times defined for this keyword
                    if not notification_minutes:
                        continue

                    # Process each notification time for this event
                    for minutes_before in notification_minutes:
                        # Calculate when the notification should be sent
                        notification_time = start_time - timedelta(minutes=minutes_before)
                        
                        # Create a unique key for this notification
                        notification_key = f"calendar_{event_id}_{notification_time.isoformat()}"
                    
                        # Check if this notification has already been sent
                        if notification_key not in sent_notifications:
                            # Calculate time difference between now and when notification should be sent
                            time_diff = abs((notification_time - now).total_seconds())
                            
                            # Log notification check details
                            print(f"\nNOTIFICATION CHECK:")
                            print(f"User: {username}")
                            print(f"   Event: {event_summary}")
                            print(f"   Alert: {minutes_before} minutes before")
                            print(f"   Notify at: {notification_time.strftime('%Y-%m-%d %H:%M')}")
                            print(f"   Time difference: {time_diff:.1f} seconds")

                            # Send notification if we're within the notification window (1 minute)
                            if time_diff <= 60:  # 1-minute window
                                # Build SMS message dynamically based on user preferences
                                message = build_event_message(event, agenda_fields)
                                    
                                # Skip if no valid fields were found to build the message
                                if not message:
                                    continue
                                
                                # Attempt to send the SMS
                                try:
                                    send_sms_raspisms(phone_number, message)
                                    # Mark this notification as sent to prevent duplicates
                                    sent_notifications.add(notification_key)
                                    print(f"SMS SENT for: {event_summary}")
                                except Exception as e:
                                    print(f"SMS ERROR: {e}")
                except Exception as event_error:
                    print(f"EVENT PROCESSING ERROR: {event_error}")

            # ------------- CLASSROOM ASSIGNMENTS PROCESSING -------------
            
            # Get upcoming assignments for this user
            assignments = get_upcoming_assignments(creds)
            
            # Process each assignment
            for assignment in assignments:
                try:
                    # Extract assignment details
                    assignment_title = assignment['title']
                    assignment_deadline = assignment['deadline']
                    classroom_course_name = assignment['course_name']
                    
                    # Define standard notification times for classroom assignments
                    # 1440 minutes = 24 hours, 60 minutes = 1 hour
                    classroom_notification_minutes = [1440, 60]
                    
                    # Log assignment details
                    print("\n" + "*"*25 + username + "*"*25)
                    print(f"CLASSROOM: {assignment_title}")
                    print(f"Course: {classroom_course_name}")
                    print(f"Deadline: {assignment_deadline.strftime('%Y-%m-%d %H:%M')}")
                    
                    # Process each notification time for this assignment
                    for classroom_minutes_before in classroom_notification_minutes:
                        # Calculate when notification should be sent
                        classroom_notification_time = assignment_deadline - timedelta(minutes=classroom_minutes_before)
                        
                        # Create unique key for this notification
                        classroom_notification_key = f"classroom_{assignment_title}_{classroom_notification_time.isoformat()}"
                        
                        # Check if this notification has already been sent
                        if classroom_notification_key not in sent_notifications:
                            # Calculate time difference between now and when notification should be sent
                            classroom_time_diff = abs((classroom_notification_time - now).total_seconds())
                            
                            # Log notification check details
                            print(f"\nCLASSROOM NOTIFICATION:")
                            print(f"   Alert: {classroom_minutes_before} minutes before")
                            print(f"   Notify at: {classroom_notification_time.strftime('%Y-%m-%d %H:%M')}")   
                            print(f"   Time difference: {classroom_time_diff:.1f} seconds")
                            
                            # Send notification if we're within the notification window (1 minute)
                            if classroom_time_diff <= 60:  # 1-minute window
                                # Create message with assignment details
                                classroom_message = f"Classroom Deadline:\n'{assignment_title}' for {classroom_course_name} is due at {assignment_deadline.strftime('%H:%M')}"
                                
                                # Attempt to send the SMS
                                try:
                                    send_sms_raspisms(phone_number, classroom_message)
                                    # Mark this notification as sent to prevent duplicates
                                    sent_notifications.add(classroom_notification_key)
                                    print(f"CLASSROOM SMS SENT for: {assignment_title}")
                                except Exception as classroom_e:
                                    print(f"CLASSROOM SMS ERROR: {classroom_e}")
                
                except Exception as classroom_assignment_error:
                    print(f"CLASSROOM PROCESSING ERROR: {classroom_assignment_error}")

            # ------------- CLEANUP -------------
            
            # Clean up old notifications (older than 24 hours) to prevent memory issues
            cutoff_time = now - timedelta(hours=24)
            sent_notifications = {
                notif for notif in sent_notifications
                if datetime.fromisoformat(notif.split('_')[-1]) >= cutoff_time
            }
        except Exception as main_error:
            print(f"MAIN ERROR: {main_error}")
        
        # Sleep before the next check cycle
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
    
    This function creates and starts a dedicated thread for monitoring
    a specific user's calendar events and classroom assignments.
    
    Args:
        user (dict): User document from MongoDB
    """
    # Extract user email for logging purposes
    email = user.get("email")
    
    # Ensure email exists before proceeding
    if not email:
        print(f"Missing email address for user: {user.get('username')}")
        return

    try:
        # Log thread creation
        print(f"Starting thread for user: {email}")
        
        # Create and start a daemon thread for this user
        # Using daemon=True ensures the thread will terminate when the main program exits
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
    
    This function sets up a MongoDB change stream to detect when new users
    are added to the database, and automatically starts monitoring threads for them.
    
    Args:
        users_collection: MongoDB collection object
    """
    print("Monitoring for new users...")
    
    # Set up a MongoDB change stream to watch for insert operations
    with users_collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
        # This loop will continue indefinitely, processing new users as they are added
        for change in stream:
            # Extract the full document of the newly inserted user
            new_user = change["fullDocument"]
            print(f"New user detected: {new_user.get('email')}")
            
            # Start a monitoring thread for this new user
            start_user_thread(new_user)

###############################################################################
# Main Function
###############################################################################

def main():
    """
    Main function to monitor new users and start threads.
    
    This function initializes the entire notification system by:
    1. Starting threads for existing users
    2. Setting up monitoring for new users
    """
    print(f"Starting IoT SMS Notification System with Algeria timezone (UTC+1)")
    
    # Start monitoring threads for all existing users in the database
    users = users_collection.find()
    for user in users:
        start_user_thread(user)

    # Set up monitoring for new users that might be added later
    watch_users_collection(users_collection)

# Entry point for the script
if __name__ == '__main__':
    main()