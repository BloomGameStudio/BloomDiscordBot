from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

class ScheduledEvent:
    def __init__(self, name, description, start_time):
        self.name = name
        self.description = description
        self.start_time = start_time
        self.interested_users = []  # Attribute to store interested users

    # Other methods and attributes for the class

def check_upcoming_events(guild):
    current_time = datetime.now().astimezone(timezone.utc)
    events = guild.scheduled_events
    upcoming_events = []

    for event in events:
        event_name = event.name
        event_description = event.description
        event_time = event.start_time
        event_user_count = event.user_count

        time_difference = event_time - current_time
        if time_difference.total_seconds() <= 24 * 3600:
            # Event is 24 hours or less away
            upcoming_events.append(event)
            print(f"Event Name: {event_name}")
            print(f"Event Description: {event_description}")
            print(f"Event Start Time: {event_time}")
            print(f"Interested Users: {(event_user_count)}")

    return upcoming_events