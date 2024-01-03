from discord.ext import commands
from shared.event_operations import handle_message, handle_reaction

def setup_shared_events(bot: commands.Bot, contributors, emoji_id_mapping, proposals, new_proposal_emoji=None):
    @bot.event
    async def on_message(message):
        await handle_message(bot, message, contributors, emoji_id_mapping, proposals)

    @bot.event
    async def on_reaction_add(reaction: bot.Reaction, user: bot.User):
        if new_proposal_emoji is not None:
            await handle_reaction(bot, reaction, user, contributors, emoji_id_mapping, proposals, new_proposal_emoji)