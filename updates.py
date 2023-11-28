from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

#May not be necessary
class ScheduledEvent:
    def __init__(self, name, description, start_time, user_count):
        self.name = name
        self.description = description
        self.start_time = start_time
        self.user_count = user_count

def format_event(event):
    return f"**Event Name:** {event.name}\n**Event ID:** {event.id}\n**Event Start Time:** {event.start_time}\n**Event Description:** {event.description}"

def get_all_events(guild):
    return guild.scheduled_events

def check_upcoming_events(guild, time_range=None):
    current_time = datetime.now().astimezone(timezone.utc)
    events = get_all_events(guild)
    upcoming_events = []
    #Check if the events start time is <= the current time
    #And >= the specified time range
    for event in events:
        if time_range:
            time_difference = event.start_time - current_time
            if 0 <= time_difference.total_seconds() <= time_range:
                upcoming_events.append(event)
        else:
            upcoming_events.append(event)

    return upcoming_events