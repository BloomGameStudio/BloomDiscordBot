from discord.ext import commands
from .event_operations import handle_on_message, handle_on_reaction_add
from constants import new_proposal_emoji
from .proposals import proposals

def setup_gov_events(bot: commands.Bot):
    @bot.event
    async def on_message(message):
        await handle_on_message(bot, message, proposals)

    @bot.event
    async def on_reaction_add(reaction, user):
        await handle_on_reaction_add(bot, user, reaction, proposals, new_proposal_emoji)
