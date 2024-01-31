import logging
from typing import Dict, Union, List
from discord.ext import commands
from discord import Message, Reaction, User
from .event_operations import (
    handle_message,
    handle_reaction
)
from .constants import RULES_MESSAGE_ID
from .event_operations import process_reaction_add, process_new_member

def setup_shared_events(
    bot: commands.Bot,
    data: Dict[str, Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]]] = {},
    proposals: List[Dict[str, str]] = [],
    new_proposal_emoji: str = "💡"
) -> None:
    @bot.event
    async def on_message(message: Message) -> None:
        await handle_message(bot, message, data, proposals)
    @bot.event
    async def on_reaction_add(reaction: Reaction, user: User) -> None:
        await handle_reaction(bot, reaction, user, data, proposals, new_proposal_emoji)

    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.message_id == RULES_MESSAGE_ID:
            await process_reaction_add(bot, payload)

    @bot.event
    async def on_member_join(member):
        logging.info(f"New member: {member.name} has joined: {member.guild.name}")
        await process_new_member(member)
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.message.channel.send("Command not found")