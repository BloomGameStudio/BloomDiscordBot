from typing import List, Dict
from discord.ext import commands
from discord import Message, Reaction, User
from shared.event_operations import handle_message, handle_reaction

def setup_shared_events(bot: commands.Bot, contributors: List[Dict[str, str]], emoji_dicts: Dict[str, Dict[str, str]], proposals: List[Dict[str, str]], new_proposal_emoji: str = "💡") -> None:
    @bot.event
    async def on_message(message: Message) -> None:
        await handle_message(bot, message, contributors, emoji_dicts, proposals)

    @bot.event
    async def on_reaction_add(reaction: Reaction, user: User) -> None:
        if new_proposal_emoji is not None:
            await handle_reaction(bot, reaction, user, contributors, emoji_dicts, proposals, new_proposal_emoji)