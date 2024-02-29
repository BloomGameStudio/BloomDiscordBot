"""
events/event_operations.py is responsible for handling the business logic associated with events
This includes fetching events, loading posted events, saving posted events, notifying guild of new events. 
"""


import json
import requests
import asyncio
import os
import discord
from consts.constants import GENERAL_CHANNEL, RULES_MESSAGE_ID, DISCORD_ROLE_TRIGGERS
from config.config import POSTED_EVENTS_FILE_PATH
from shared.helpers import get_channel_by_name, send_dm_once
from datetime import datetime, timezone
from typing import List, Optional, Any, Dict, Union
from discord import ScheduledEvent, Reaction, User, Message
from discord.utils import get
from discord.ext.commands import Bot
from discord.ext import commands
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
        await asyncio.sleep(1 * 60)

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

async def process_new_member(member: discord.Member) -> None:
    """
    Sends a welcome message to a new member in the welcome channel.

    Args:
        member (discord.Member): The new member who joined the server.
    """
    try:
        # Get the welcome channel
        welcome_channel = get_channel_by_name(member.guild, GENERAL_CHANNEL)
        collab_land_join_channel = get_channel_by_name(member.guild, "collabland-join")
        start_here_channel = get_channel_by_name(member.guild, "start-here")

        # Send the welcome message
        await welcome_channel.send(
            f" 🌺 Welcome {member.mention}  to {member.guild.name}! We are pleased to have you here 🌺\n"
            "\n"
            "Take a moment to read and agree to the rules before you get started!"
            "\n"
            f"If you are an existing aXP, bXP, or uXP Hodler, please head over to <#{collab_land_join_channel.id}> to verify your wallet in order to receive your respective role! \n"
            "\n"
            f"Refer to <#{start_here_channel.id}> for more details about the studio!"
        )
    except ValueError as e:
        logger.error(f"Error sending welcome message: {str(e)}")


async def handle_message(
    bot: commands.Bot,
    message: Message,
    data: Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]],
    proposals: List[Dict[str, Union[str, int]]],
) -> None:
    """
    Handles a new message in the server.
    If a contributors emoji is found, a DM is sent to the contributor.

    Args:
        bot (commands.Bot): The bot instance.
        message (Message): The new message.
        data (Dict): The server data.
        proposals (List): The list of proposals.
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    server_name = message.guild.name
    server_data = data["servers"].get(server_name)

    # Log a warning if no data is found for the server
    if server_data is None:
        logger.warning(f"No data found for server: {server_name}")
        return

    contributors = server_data["contributors"]
    emoji_dicts = server_data["emoji_dictionary"]

    # Check if any emoji in the message matches an emoji in the emoji dictionary
    for emoji_id, contributor_uid in emoji_dicts.items():
        contributor = next(
            (c for c in contributors if c["uid"] == contributor_uid), None
        )
        if emoji_id in message.content:
            logger.info("Emoji Found in message! %s", emoji_id)
            if contributor and str(contributor["uid"]) != str(
                message.author.id
            ):  # Convert both IDs to strings before comparing
                try:
                    logger.info(f'Messaging the user, {contributor["uid"]}')
                    message_link = message.jump_url
                    await send_dm_once(bot, contributor, message_link)
                except discord.errors.NotFound:
                    logger.warning(f'User not found: {contributor["uid"]}')

async def handle_reaction(
    bot: commands.Bot,
    reaction: Reaction,
    user: User,
    data: Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]],
    proposals: List[Dict[str, Union[str, int]]],
) -> None:
    """
    Handles a new reaction in the server.
    If a contributors emoji is found, a DM is sent to the contributor.

    Args:
        bot (commands.Bot): The bot instance.
        reaction (Reaction): The new reaction.
        user (User): The user who added the reaction.
        data (Dict): The server data.
        proposals (List): The list of proposals.
        new_proposal_emoji (str): The emoji for new proposals.
    """
    # Get the server name and data
    server_name = reaction.message.guild.name
    server_data = data["servers"].get(server_name)

    # Log a warning if no data is found for the server
    if server_data is None:
        logger.warning(f"No data found for server: {server_name}")
        return

    # Ignore reactions from the bot itself
    if user == bot.user:
        return

    contributors = server_data["contributors"]
    emoji_dicts = server_data["emoji_dictionary"]

    # Check if the reaction emoji matches any in the emoji dictionary
    contributor_emoji = next(
        (
            emoji_id
            for emoji_id, contributor_uid in emoji_dicts.items()
            if str(reaction.emoji) == emoji_id
        ),
        None,
    )

    # If a matching emoji is found, send a DM to the contributor
    if contributor_emoji:
        contributor = next(
            (c for c in contributors if c["uid"] == emoji_dicts[contributor_emoji]),
            None,
        )
        if contributor and str(contributor["uid"]) != str(
            user.id
        ):  # Check if the user who reacted is not the contributor
            message_link = reaction.message.jump_url
            logger.info("Emoji react found, DMing contributor")
            await send_dm_once(bot, contributor, message_link)


async def process_reaction_add(bot, payload):
    """
    Processes a reaction add event. Allocates roles to members based on their reaction.

    Args:
        bot (commands.Bot): The bot instance.
        payload (discord.RawReactionActionEvent): The reaction payload.
    """
    # If the reaction is on the rules message, process the reaction
    if payload.message_id == RULES_MESSAGE_ID:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        # If the reaction emoji is "🌺", add the "bloomer" role to the member
        if payload.emoji.name == "🌺":
            role = get(guild.roles, name="bloomer")
            await member.add_roles(role)
            response = f"{member.display_name} has selected 🌺!\n\n**Their commitment is official and they are now a Bloomer!**"
            general_channel = get_channel_by_name(guild, "🌺│home")
            await general_channel.send(response)
        else:
            # If the reaction emoji matches any in DISCORD_ROLE_TRIGGERS, add the corresponding role to the member
            for role_info in DISCORD_ROLE_TRIGGERS:
                if payload.emoji.id == role_info.get("emoji_id"):
                    general_channel = get_channel_by_name(guild, "🌺│home")
                    role = get(guild.roles, name=role_info.get("role"))
                    response = f"{member.display_name} has joined the **{role_info.get('name')}** pod!"
                    await general_channel.send(response)

                    if role is None:
                        logger.info(f"Role {role_info.get('role')} not found")
                        return
                    await member.add_roles(role)
