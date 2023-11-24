#When an event is deleted, it should be detected, and removed from updates.json
#Format time etc in Discord formatting
#Is Discord formatting applicable to the emotes/emojis
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

# JSON Encoding for dealing with datetime format
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Load scheduled events from updates.json
def load_scheduled_events():
    try:
        with open('updates.json', 'r') as file:
            data = json.load(file)
            # Convert start_time to datetime objects
            for event_id, event_info in data.items():
                event_info['start_time'] = datetime.fromisoformat(event_info['start_time'])
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save scheduled events to updates.json
def save_scheduled_events():
    with open('updates.json', 'w') as file:
        json.dump(scheduled_events, file, indent=4, cls=DateTimeEncoder)

# Dictionary to store scheduled events
scheduled_events = load_scheduled_events()


# Function to post event details 24 hours before it begins
async def post_event_details(bot):
    print("Checking for scheduled events")
    print(f'Number of scheduled events: {len(scheduled_events)}')

    for event_id, event_info in scheduled_events.items():
        start_time = event_info['start_time'].replace(tzinfo=timezone.utc)  # Make start_time timezone-aware
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)  # Make current_time timezone-aware
        # Check if the event is scheduled within the next 24 hours
        if start_time - current_time <= timedelta(hours=24) and start_time > current_time:
            print(f"Event '{event_info['name']}' is scheduled within the next 24 hours")
            general_channel = bot.get_channel(os.getenv('CHANNEL_ID'))
            
            # Check if the channel exists and the bot has permission to send messages
            if general_channel:
                await general_channel.send(f"Events in 24 hours or less!\n**Event Name:** {event_info['name']}\n**Start Time:** {start_time}")
            else:
                print("General channel not found or bot doesn't have permission to send messages.")


# Function to load scheduled events and post details
async def load_and_post_events(bot):
    await bot.wait_until_ready()  # Wait until the bot is fully connected and ready

    # Load scheduled events before starting the bot
    scheduled_events = load_scheduled_events()
    await post_event_details()


