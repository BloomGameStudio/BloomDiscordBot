"""
The "EventOperations" class is responsible for handling event operations.
Refer to the classes functions for more information on what they do.
"""

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
from utils.utils import Utils, DiscordUtils
from datetime import datetime, timezone
from typing import List, Optional, Any
from discord import ScheduledEvent, Reaction, User
from discord.utils import get
from discord.ext import commands
from logger.logger import logger


class EventOperations:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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

    async def notify_new_event(self, event: ScheduledEvent, guild_id: int) -> None:
        """
        Notify the General channel about the newly created event after a short delay.
        """
        logger.info(
            f"Starting notify_new_event for event {event.name} in guild {guild_id}"
        )
        guild = self.bot.get_guild(guild_id)

        if guild:
            logger.info(f"Found guild {guild.name}, waiting 60 seconds...")
            await asyncio.sleep(30 * 60)
            event = await guild.fetch_scheduled_event(event.id)
            formatted_event = self.format_event(event, guild_id)
            logger.info(f"Formatted event message: {formatted_event}")

            try:
                channel = await DiscordUtils.get_channel_by_name(guild, GENERAL_CHANNEL)
                if channel:
                    logger.info(f"Found channel {channel.name}, sending message...")
                    await channel.send(
                        f"🌺 **__Newly Created Event__** 🌺 \n{formatted_event}"
                    )
                    logger.info("Event notification sent successfully")
                else:
                    logger.error(f"Channel not found in guild {guild.name}")
            except Exception as e:
                logger.error(f"Cannot post newly created event to Discord, Error: {e}")
        else:
            logger.error(f"Guild not found: {guild_id}")

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
        """
        try:
            welcome_channel = await DiscordUtils.get_channel_by_name(
                member.guild, GENERAL_CHANNEL
            )
            collab_land_join_channel = await DiscordUtils.get_channel_by_name(
                member.guild, COLLAB_LAND_CHANNEL
            )
            start_here_channel = await DiscordUtils.get_channel_by_name(
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
        except Exception as e:
            logger.error(f"Error sending welcome message: {str(e)}")

    async def handle_message(self, message: discord.Message) -> None:
        """
        Handles a new message in the server.
        If a contributor's emoji is found, a DM is sent to them.

        Parameters:
        message (Message): The new message.
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

        contributors = Utils.get_contributors_from_db(message.guild.id)
        for contributor in contributors:
            if contributor.emoji_id in message.content and str(contributor.uid) != str(
                message.author.id
            ):
                try:
                    logger.info(f"Messaging the user, {contributor.uid}")
                    message_link = message.jump_url
                    user = await self.bot.fetch_user(int(contributor.uid))
                    if user:
                        await Utils.send_dm_once(self.bot, user, message_link)
                except discord.errors.NotFound:
                    logger.warning(f"User not found: {contributor.uid}")

    async def handle_reaction(self, reaction: Reaction, user: User) -> None:
        """
        Handles a new reaction in the server.
        If a contributor's emoji is found, a DM is sent to them.

        Parameters:
        reaction (Reaction): The new reaction.
        user (User): The user who added the reaction.
        """
        contributors = Utils.get_contributors_from_db(reaction.message.guild.id)

        contributor = next(
            (c for c in contributors if str(reaction.emoji) == c.emoji_id), None
        )

        if contributor and str(contributor.uid) != str(user.id):
            message_link = reaction.message.jump_url
            try:
                contributor_user = await self.bot.fetch_user(int(contributor.uid))
                if contributor_user:
                    await Utils.send_dm_once(self.bot, contributor_user, message_link)
            except discord.errors.NotFound:
                logger.warning(f"User not found: {contributor.uid}")

    async def process_reaction_add(self, payload) -> None:
        """
        Process a reaction add event.
        If the reaction is added to the rules message, assign the corresponding role.

        Parameters:
        payload: The payload for the reaction add event.
        """
        if payload.message_id == RULES_MESSAGE_ID:
            guild = self.bot.get_guild(payload.guild_id)
            if guild:
                member = guild.get_member(payload.user_id)
                if member:
                    role_name = DISCORD_ROLE_TRIGGERS.get(str(payload.emoji))
                    if role_name:
                        role = get(guild.roles, name=role_name)
                        if role:
                            await member.add_roles(role)
                            logger.info(
                                f"Added role {role_name} to member {member.name}"
                            )
