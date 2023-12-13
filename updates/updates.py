from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import asyncio
import json

load_dotenv()

def load_posted_events():
    try:
        # Assuming main.py is one level up from the updates directory
        file_path = os.path.join(os.path.dirname(__file__), "..", "updates", "posted_events.json")
        print(f"Loading events from: {file_path}")
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_posted_events(posted_events):
    try:
        # Assuming main.py is one level up from the updates directory
        file_path = os.path.join(os.path.dirname(__file__), "..", "updates", "posted_events.json")
        print(f"Saving events to: {file_path}")
        with open(file_path, "w") as file:
            json.dump(posted_events, file)
    except Exception as e:
        print(f"Error saving posted events: {e}")

def format_event(event):
    # Format the event start time for Discord time
    guild_id = int(os.getenv("GUILD_ID"))
    event_url = f"https://discord.com/events/{guild_id}/{event.id}"

    formatted_event = (
        f"\n"
        f"🌺**{event.name}**🌺\n"
        #f"**Event Start Time @ ** {formatted_start_time}\n"
        #f"**Event Description:** {event.description}\n"
        #f"{event.image}"
        f"To request someones attendance, react to this message with their emoji! \n"
        f":link:**Event Link:link: ** {event_url}\n"
    )
    return formatted_event

async def notify_new_event(bot, event):
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        # Wait for 60 mins before sending the notification
        await asyncio.sleep(60)

        # Fetch the event again to get the updated details
        event = await guild.fetch_scheduled_event(event.id)
        formatted_event = format_event(event)

        channel_id = int(os.getenv("GENERAL_CHANNEL_ID"))
        channel = guild.get_channel(channel_id)

        if channel:
            # Send the notification and capture the Message object
            message = await channel.send(f"**Newly Created Event**:\n{formatted_event}")

            # Get the message ID and print it
            message_id = message.id
            print(f"Message ID of the notification: {message_id}")
        else:
            print(f"Event channel not found")
    else:
        print(f"Guild not found")

def get_all_events(guild):
    return guild.scheduled_events

async def check_upcoming_events(guild, time_range=None):
    current_time = datetime.now().astimezone(timezone.utc)
    events = get_all_events(guild)
    upcoming_events = []

    # Check if the events start time is <= the current time
    # And >= the specified time range
    for event in events:
        if time_range:
            # Fetch the event again to get the updated user_count
            event = await guild.fetch_scheduled_event(event.id)

            time_difference = event.start_time - current_time
            if 0 <= time_difference.total_seconds() <= time_range:
                upcoming_events.append(event)
        else:
            upcoming_events.append(event)

    return upcoming_events
