"""
shared/events.py is responsible for setting up the shared events for the bot.
shared events may be events that contain functionality that is used by multiple
modules. For example, the on_message event is used by the gov and emotes modules.

"""

from logger.logger import logger
from typing import Dict, Union, List
from discord.ext import commands
from discord import Message, Reaction, User
from consts.constants import RULES_MESSAGE_ID
from .event_operations import handle_message, handle_reaction, process_new_member, process_reaction_add


def setup_shared_events(
    bot: commands.Bot,
    data: Dict[
        str, Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]]
    ] = {},
    proposals: List[Dict[str, str]] = [],
) -> None:
    """
    Sets up shared events for the bot.

    Parameters:
    bot (commands.Bot): The bot to which the events are being added.
    data (Dict): A dictionary containing data related to the events.
    proposals (List[Dict[str, str]]): A list of proposals related to the events.
    new_proposal_emoji (str): The emoji used to indicate a new proposal.

    Returns:
    None
    """

    @bot.event
    async def on_message(message: Message) -> None:
        """
        Event triggered when a message is sent in a server the bot is in.

        Parameters:
        message (Message): The message that was sent.

        Returns:
        None
        """
        await handle_message(bot, message, data, proposals)

    @bot.event
    async def on_reaction_add(reaction: Reaction, user: User) -> None:
        """
        Event triggered when a reaction is added to a message in a server the bot is in.

        Parameters:
        reaction (Reaction): The reaction that was added.
        user (User): The user who added the reaction.

        Returns:
        None
        """
        await handle_reaction(bot, reaction, user, data, proposals)

    @bot.event
    async def on_raw_reaction_add(payload):
        """
        Event triggered when a raw reaction is added to a message in a server the bot is in.

        Parameters:
        payload: The payload for the raw reaction add event.

        Returns:
        None
        """
        if payload.message_id == RULES_MESSAGE_ID:
            await process_reaction_add(bot, payload)

    @bot.event
    async def on_member_join(member):
        """
        Event triggered when a new member joins a server the bot is in.

        Parameters:
        member: The member who joined.

        Returns:
        None
        """
        logger.info(f"New member: {member.name} has joined: {member.guild.name}")
        await process_new_member(member)

    @bot.event
    async def on_command_error(ctx, error):
        """
        Event triggered when a command error occurs.

        Parameters:
        ctx: The context in which the command was invoked.
        error: The error that occurred.

        Returns:
        None
        """
        if isinstance(error, commands.CommandNotFound):
            await ctx.message.channel.send("Command not found")
