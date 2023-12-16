from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from shared.shared import logging
import os
import asyncio
import json
import requests

load_dotenv()
      
def load_posted_events():
    try:
        file_path = os.path.join(os.path.dirname(__file__), "..", "updates", "posted_events.json")
        logging.info(f"Loading events from: {file_path}")
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_posted_events(posted_events):
    try:
        file_path = os.path.join(os.path.dirname(__file__), "..", "updates", "posted_events.json")

        logging.info(f"Saving events to: {file_path}")

        with open(file_path, "w") as file:
            json.dump(posted_events, file)
            
    except Exception as e:
        logging.error(f"Error saving posted events: {e}")
    
def format_event(event):
    # Format the event start time for Discord time
    guild_id = int(os.getenv("GUILD_ID"))
    event_url = f"https://discord.com/events/{guild_id}/{event.id}"

    formatted_event = (
        f"\n"
        f" **{event.name}**\n"
        f"\n"
        f"To request someones attendance, react to this message with their emoji! \n"
        f"\n"
        f":link:** Event Link** {event_url} :link:\n"
    )
    return formatted_event

async def notify_new_event(bot, event):
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        # Wait for 30 mins before sending the notification
        await asyncio.sleep(60 * 30)

        # Fetch the event again to get the updated details
        event = await guild.fetch_scheduled_event(event.id)
        formatted_event = format_event(event)

        channel_id = int(os.getenv("GENERAL_CHANNEL_ID"))
        channel = guild.get_channel(channel_id)

        if channel:
            # Send the notification and capture the Message object
            await channel.send(f"🌺 **__Newly Created Event__** 🌺 \n{formatted_event}")

        else:
            logging.info(f"Event channel not found")
    else:
        logging.info(f"Guild not found")

def get_all_events(guild):
    return guild.scheduled_events

async def check_upcoming_events(guild, time_range=None):
    current_time = datetime.now().astimezone(timezone.utc)
    events = get_all_events(guild)
    upcoming_events = []

    # Check if the event's start time is in the future (after or equal to the current time)
    # And if a time range is specified, ensure the time difference is within that range
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

# NOTE: For some reason it doesn't appear that you can access the userIDs interested
# in a scheduled event. It's either a count, or a boolean.
# performing a GET request, however, does allow this.
def get_guild_scheduled_event_users(guild_id, scheduled_event_id, limit=100, with_member=False, before=None, after=None):
    url = f"https://discord.com/api/v10/guilds/{guild_id}/scheduled-events/{scheduled_event_id}/users"

    params = {
        'limit': limit,
        'with_member': with_member,
        'before': before,
        'after': after
    }

    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    headers = {
        'Authorization': f'Bot {bot_token}'
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None