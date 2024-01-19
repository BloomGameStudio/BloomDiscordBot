from typing import Dict, Union, List
from discord.ext import commands
from discord import Message, Reaction, User
from shared.event_operations import handle_message, handle_reaction


def setup_shared_events(
    bot: commands.Bot,
    data: Dict[str, Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]]],
    proposals: List[Dict[str, str]],
    new_proposal_emoji: str = "💡",
) -> None:
    @bot.event
    async def on_message(message: Message) -> None:
        await handle_message(bot, message, data, proposals)

    @bot.event
    async def on_reaction_add(reaction: Reaction, user: User) -> None:
        if new_proposal_emoji is not None:
            await handle_reaction(
                bot, reaction, user, data, proposals, new_proposal_emoji
            )
