from typing import Dict, Union, List
from discord.ext import commands
from discord import Message, Reaction, User
from discord.utils import get
from shared.event_operations import handle_message, handle_reaction
import logging

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
    @bot.event
    async def on_member_join(member):
        logging.info(f"New member: {member.name} in server: {member.guild.name}")
        unverified_role = get(member.guild.roles, name="unverified")
        if unverified_role:
            await member.add_roles(unverified_role)

        await member.send("Welcome to Bloom Collective! Please read the rules in #welcome-and-rules and introduce yourself in #introductions. You can also check out our website at https://bloomcollective.org/ and our wiki at https://wiki.bloomcollective.org/")