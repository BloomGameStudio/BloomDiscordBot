"""
The "EventOperations" class is responsible for handling event operations.
Refer to the classes functions for more information on what they do.
"""

import json
import requests
import asyncio
import os
import discord
from consts.constants import (
    GENERAL_CHANNEL,
    RULES_MESSAGE_ID,
    DISCORD_ROLE_TRIGGERS,
    COLLAB_LAND_CHANNEL,
    START_HERE_CHANNEL,
)
from config.config import POSTED_EVENTS_FILE_PATH
from utils.utils import Utils
from datetime import datetime, timezone
from typing import List, Optional, Any, Dict
from discord import ScheduledEvent, Reaction, User
from discord.utils import get
from discord.ext import commands
from logger.logger import logger


class EventOperations:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def save_posted_events(self, posted_events: List[int]) -> None:
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

    def format_event(self, event: ScheduledEvent, guild_id: int) -> str:
        """
        Formats the event message and returns it.
        Invoked by notify_new_event.

        Parameters:
        event (ScheduledEvent): The event to be formatted.
        guild_id (int): The ID of the guild in which the event was created.

        Returns:
        str: The formatted event message.
        """
        event_url = f"https://discord.com/events/{guild_id}/{event.id}"
        formatted_event = (
            f"\n"
            f" **{event.name}**\n"
            f"\n"
            f"To request someone's attendance, react to this message with their emoji! \n"
            f"\n"
            f":link: ** Event Link {event_url} **:link:\n"
        )
        return formatted_event

    def get_guild_scheduled_event_users(
        self,
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
            logger.error(f"Error: {response.status_code} - {response.text}")
            return None

    async def notify_new_event(
        self, event: discord.ScheduledEvent, guild_id: int
    ) -> None:
        """
        Notify the General channel about the newly created event after a short delay.

        Parameters:
        event (ScheduledEvent): The event to be notified.
        guild_id (int): The ID of the guild in which the event was created.
        """
        guild = self.bot.get_guild(guild_id)

        if guild:
            await asyncio.sleep(30 * 60)
            event = await guild.fetch_scheduled_event(event.id)
            formatted_event = self.format_event(event, guild_id)

            try:
                channel = Utils.get_channel_by_name(guild, GENERAL_CHANNEL)
                await channel.send(
                    f"🌺 **__Newly Created Event__** 🌺 \n{formatted_event}"
                )
            except ValueError as e:
                logger.error(f"Cannot post newly created event to Discord, Error: {e}")
        else:
            logger.info(f"Guild not found")

    async def fetch_upcoming_events(self, guild):
        """
        Fetches all upcoming events within the next 24 hours.

        Parameters:
        guild (Guild): The guild for which the events are to be fetched.

        Returns:
        List[ScheduledEvent]: The list of upcoming events.
        """
        current_time = datetime.now().astimezone(timezone.utc)
        events = await guild.fetch_scheduled_events()
        upcoming_events = [
            event
            for event in events
            if 0 <= (event.start_time - current_time).total_seconds() <= 24 * 3600
        ]
        return upcoming_events

    async def process_new_member(self, member: discord.Member) -> None:
        """
        Sends a welcome message to a new member in the welcome channel.

        Parameters:
        member (discord.Member): The new member who joined the server.
        """
        try:
            welcome_channel = Utils.get_channel_by_name(member.guild, GENERAL_CHANNEL)
            collab_land_join_channel = Utils.get_channel_by_name(
                member.guild, COLLAB_LAND_CHANNEL
            )
            start_here_channel = Utils.get_channel_by_name(
                member.guild, START_HERE_CHANNEL
            )

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
        self, message: discord.Message, emoji_dicts: Dict[str, Dict[str, str]]
    ) -> None:
        """
        Handles a new message in the server.
        If a contributor's emoji is found, a DM is sent to them.

        Parameters:
        message (Message): The new message.
        emoji_dicts (Dict[str, Dict[str, str]]): The dictionary of emoji to user mappings for each server.
        """
        if message.content.lower().startswith(".update_commands"):
            try:
                logger.info("Updating commands")
                await self.bot.tree.sync()
                logger.info("Commands updated")
            except Exception as e:
                logger.error(f"Error updating commands: {e}")

        if message.author == self.bot.user:
            return

        server_name = message.guild.name
        emoji_dict = emoji_dicts[server_name]

        for emoji_id, user_id in emoji_dict.items():
            if emoji_id in message.content and str(user_id) != str(message.author.id):
                try:
                    logger.info(f"Messaging the user, {user_id}")
                    message_link = message.jump_url
                    user = await self.bot.fetch_user(int(user_id))
                    if user:
                        await Utils.send_dm_once(self.bot, user, message_link)
                except discord.errors.NotFound:
                    logger.warning(f"User not found: {user_id}")

    async def handle_reaction(
        self, reaction: Reaction, user: User, emoji_dicts: Dict[str, Dict[str, str]]
    ) -> None:
        """
        Handles a new reaction in the server.
        If a contributor's emoji is found, a DM is sent to them.

        Parameters:
        reaction (Reaction): The new reaction.
        user (User): The user who added the reaction.
        emoji_dicts (Dict[str, Dict[str, str]]): The dictionary of emoji to user mappings for each server.
        """
        server_name = reaction.message.guild.name
        server_emoji_dict = emoji_dicts.get(server_name)

        if not server_emoji_dict:
            logger.warning(f"No emoji dictionary found for the server: {server_name}")
            return

        contributor_emoji = next(
            (
                emoji_id
                for emoji_id, contributor_uid in server_emoji_dict.items()
                if str(reaction.emoji) == emoji_id
            ),
            None,
        )

        if contributor_emoji:
            contributor_uid = server_emoji_dict.get(contributor_emoji)
            if contributor_uid and str(contributor_uid) != str(user.id):
                message_link = reaction.message.jump_url
                try:
                    contributor_user = await self.bot.fetch_user(int(contributor_uid))
                    if contributor_user:
                        await Utils.send_dm_once(
                            self.bot, contributor_user, message_link
                        )
                except discord.errors.NotFound:
                    logger.warning(f"User not found: {contributor_uid}")

    async def process_reaction_add(self, payload) -> None:
        """
        Processes a reaction add event. Allocates roles to members based on their reaction.

        Parameters:
        payload (discord.RawReactionActionEvent): The reaction payload.

        Returns:
        None
        """
        if payload.message_id == RULES_MESSAGE_ID:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            if payload.emoji.name == "🌺":
                role = get(guild.roles, name="bloomer")
                await member.add_roles(role)
                response = f"{member.display_name} has selected 🌺!\n\n**Their commitment is official and they are now a Bloomer!**"
                general_channel = Utils.get_channel_by_name(guild, "🌺│home")
                await general_channel.send(response)
            else:
                for role_info in DISCORD_ROLE_TRIGGERS:
                    if payload.emoji.id == role_info.get("emoji_id"):
                        general_channel = Utils.get_channel_by_name(guild, "🌺│home")
                        role = get(guild.roles, name=role_info.get("role"))
                        response = f"{member.display_name} has joined the **{role_info.get('name')}** pod!"
                        await general_channel.send(response)

                        if role is None:
                            logger.info(f"Role {role_info.get('role')} not found")
                            return
                        await member.add_roles(role)
