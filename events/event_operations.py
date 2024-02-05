"""
events/event_operations.py is responsible for handling the business logic associated with events
This includes fetching events, loading posted events, saving posted events, notifying guild of new events. 
"""


import json
import requests
import asyncio
import os
from consts.constants import POSTED_EVENTS_FILE_PATH, GENERAL_CHANNEL
from shared.helpers import get_channel_by_name
from datetime import datetime, timezone
from typing import List, Optional, Any
from discord import ScheduledEvent
from discord.ext.commands import Bot
from logger.logger import logger


# Load the stored events from the JSON file
def load_posted_events() -> List[int]:
    """
    Load the event IDs that have already been posted to Discord from the JSON file.

    Returns:
    List[int]: The list of event IDs that have already been posted to Discord.
    """
    try:
        logger.info(f"Loading events from: {POSTED_EVENTS_FILE_PATH}")
        with open(POSTED_EVENTS_FILE_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


# Save the posted events to the JSON file
def save_posted_events(posted_events: List[int]) -> None:
    """
    Save the posted event IDs to the JSON file.

    Parameters:
    posted_events (List[int]): The list of event IDs that have already been posted to Discord.
    """
    try:
        logger.info(f"Saving events to: {POSTED_EVENTS_FILE_PATH}")

        with open(POSTED_EVENTS_FILE_PATH, "w") as file:
            json.dump(posted_events, file)

    except Exception as e:
        logger.error(f"Error saving posted events: {e}")


# Format the event message and send it to the channel
def format_event(event: ScheduledEvent, guild_id: int) -> str:
    """
    Formats the event message and returns it.
    invoked by notify_new_event

    Parameters:
    event (ScheduledEvent): The event to be formatted.
    guild_id (int): The ID of the guild in which the event was created.

    Returns:
    str: The formatted event message.
    """
    # Format the event start time for Discord time
    event_url = f"https://discord.com/events/{guild_id}/{event.id}"

    formatted_event = (
        f"\n"
        f" **{event.name}**\n"
        f"\n"
        f"To request someones attendance, react to this message with their emoji! \n"
        f"\n"
        f":link: ** Event Link {event_url} **:link:\n"
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
    """
    Get the users interested in a scheduled event.

    Parameters:
    guild_id (int): The ID of the guild in which the event was created.
    scheduled_event_id (int): The ID of the event.
    limit (int): The maximum number of users to be returned.
    NOTE: The remaining below are optional parameters, that we may wish to use in the future.
    with_member (bool): Whether to include the member object in the response.
    before (Optional[str]): The ID of the user to be used as the upper limit.
    after (Optional[str]): The ID of the user to be used as the lower limit.

    Returns:
    Optional[List[Any]]: The list of users interested in the event.
    """
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
    """
    Notify the General channel about the newly created event after a short delay.
    Fetches and formats the event before posting it.

    Parameters:
    bot (Bot): The bot instance.
    event (ScheduledEvent): The event that was created.
    guild_id (int): The ID of the guild in which the event was created.
    """

    guild = bot.get_guild(guild_id)

    if guild:
        # Wait for 30 mins before sending the notification
        await asyncio.sleep(30 * 60)

        # Fetch the event again to get the updated details
        event = await guild.fetch_scheduled_event(event.id)
        formatted_event = format_event(event, guild_id)

        try:
            channel = get_channel_by_name(guild, GENERAL_CHANNEL)
            # Send the notification and capture the Message object
            await channel.send(f"🌺 **__Newly Created Event__** 🌺 \n{formatted_event}")
        except ValueError as e:
            logger.error(f"Cannot post newly created event to Discord, Error: {e}")
            return

    else:
        logger.info(f"Guild not found")


# Fetch all upcoming events within the next 24 hours this is called by tasks.py
async def fetch_upcoming_events(guild):
    """
    Fetches all upcoming events within the next 24 hours.

    Parameters:
    guild (Guild): The guild for which the events are to be fetched.

    Returns:
    List[ScheduledEvent]: The list of upcoming events.

    """
    current_time = datetime.now().astimezone(timezone.utc)
    events = await guild.fetch_scheduled_events()
    upcoming_events = []

    for event in events:
        time_difference = event.start_time - current_time
        if 0 <= time_difference.total_seconds() <= 24 * 3600:
            upcoming_events.append(event)

    return upcoming_events
