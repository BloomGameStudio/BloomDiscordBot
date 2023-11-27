import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

# JSON Encoding for dealing with datetime format for updates.json
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

# Function to cleanup updates.json by removing events that have already occurred
def cleanup_scheduled_events():
    global scheduled_events
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    # Filter out events that have already occurred
    scheduled_events = {event_id: event_info for event_id, event_info in scheduled_events.items() if event_info['start_time'] > current_time}
    # Save the cleaned-up scheduled events to updates.json
    save_scheduled_events()

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
            channel_id = int(os.getenv('CHANNEL_ID'))
            # Check if the channel exists and the bot has access to it
            general_channel = bot.get_channel(channel_id)
            if general_channel:
                await general_channel.send(f"Events in 24 hours or less!\n**Event Name:** {event_info['name']}\n**Start Time:** {start_time}")
            else:
                print("General channel not found or bot doesn't have permission to send messages.")
        else:
            # If the event has already occurred, cleanup the updates.json
            cleanup_scheduled_events()

# Function to load and post events with a periodic cleanup
async def load_and_post_events(bot):
    await bot.wait_until_ready()
    # Load scheduled events before starting the bot
    global scheduled_events  # Use the global variable
    scheduled_events = load_scheduled_events()
    while not bot.is_closed():
        await post_event_details(bot)
        await asyncio.sleep(60 * 60 * 24)  # Sleep for 24 hours before the next iteration
