import logging
from typing import Dict, Union, List
from discord.ext import commands
from discord import Message, Reaction, User
from shared.event_operations import (
    handle_message,
    handle_reaction
)
from controllers.command_manager import CommandManager
from controllers.data_manager import DataManager
from controllers.settings import Settings
from controllers.crypto_constants import RULES_MESSAGE_ID

def setup_shared_events(
    bot: commands.Bot,
    command_manager: CommandManager,
    data_manager: DataManager,
    settings: Settings,
    data: Dict[str, Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]]] = {},
    proposals: List[Dict[str, str]] = [],
    new_proposal_emoji: str = "💡"
) -> None:
    @bot.event
    async def on_message(message: Message) -> None:
        await handle_message(bot, message, data, proposals, command_manager, data_manager, settings)
    @bot.event
    async def on_reaction_add(reaction: Reaction, user: User) -> None:
        logging.info(f"Reaction added: {reaction.emoji}")
        await handle_reaction(bot, reaction, user, data, proposals, new_proposal_emoji)

    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.message_id == RULES_MESSAGE_ID:
            await command_manager.process_reaction_add(bot, payload)

    @bot.event
    async def on_member_join(member):
        logging.info(f"New member: {member.name} has joined: {member.guild.name}")
        await command_manager.process_new_member(member)
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            logging.info(f"An invalid command '{ctx.message.content}' was sent, it may be processed under on_message instead")
            return