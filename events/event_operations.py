import json
import requests
import logging
import asyncio
import os
from shared.constants import POSTED_EVENTS_FILE_PATH, GENERAL_CHANNEL
from shared.helpers import get_channel_by_name
from datetime import datetime, timezone
from typing import List, Optional, Any
from discord import ScheduledEvent
from discord.ext.commands import Bot


# Load the stored events from the JSON file
def load_posted_events() -> List[int]:
    try:
        logging.info(f"Loading events from: {POSTED_EVENTS_FILE_PATH}")
        with open(POSTED_EVENTS_FILE_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


# Save the posted events to the JSON file
def save_posted_events(posted_events: List[int]) -> None:
    try:
        logging.info(f"Saving events to: {POSTED_EVENTS_FILE_PATH}")

        with open(POSTED_EVENTS_FILE_PATH, "w") as file:
            json.dump(posted_events, file)

    except Exception as e:
        logging.error(f"Error saving posted events: {e}")


# Format the event message and send it to the channel
def format_event(event: ScheduledEvent, guild_id: int) -> str:
    # Format the event start time for Discord time
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


# NOTE: For some reason it doesn't appear that you can access the userIDs interested
# in a scheduled event. It's either a count, or a boolean.
# performing a GET request, however, does allow this.
def get_guild_scheduled_event_users(
    guild_id: int,
    scheduled_event_id: int,
    limit: int = 100,
    with_member: bool = False,
    before: Optional[str] = None,
    after: Optional[str] = None,
) -> Optional[List[Any]]:
    url = f"https://discord.com/api/v10/guilds/{guild_id}/scheduled-events/{scheduled_event_id}/users"

    params = {
        "limit": limit,
        "with_member": with_member,
        "before": before,
        "after": after,
    }

    headers = {"Authorization": f'Bot {os.getenv("DISCORD_BOT_TOKEN")}'}

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


# Notify the channel about the newly created event after a short delay
async def notify_new_event(bot: Bot, event: ScheduledEvent, guild_id: int) -> None:
    guild = bot.get_guild(guild_id)

    if guild:
        # Wait for 30 mins before sending the notification
        await asyncio.sleep(30 * 60)

        # Fetch the event again to get the updated details
        event = await guild.fetch_scheduled_event(event.id)
        formatted_event = format_event(event, guild_id)

        channel = get_channel_by_name(guild, GENERAL_CHANNEL)

        if channel:
            # Send the notification and capture the Message object
            await channel.send(f"🌺 **__Newly Created Event__** 🌺 \n{formatted_event}")

        else:
            logging.info(f"Event channel not found for guild.")
    else:
        logging.info(f"Guild not found")


# Fetch all upcoming events within the next 24 hours this is called by tasks.py
async def fetch_upcoming_events(guild):
    current_time = datetime.now().astimezone(timezone.utc)
    events = await guild.fetch_scheduled_events()
    upcoming_events = []

    for event in events:
        time_difference = event.start_time - current_time
        if 0 <= time_difference.total_seconds() <= 24 * 3600:
            upcoming_events.append(event)

    return upcoming_events