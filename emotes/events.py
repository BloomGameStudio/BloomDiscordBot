from discord.ext import commands
from emotes.event_operations import handle_message, handle_reaction

"""
The below events are used to handle messages and reactions.
The function calls related to the events are located in event_operations.py
setup_event_events is used so that all event events can be loaded at once. instead of individually.
"""

def setup_contributor_events(bot: commands.Bot, contributors, emoji_id_mapping):
    @bot.event
    async def on_message(message):
        await handle_message(bot, message, contributors, emoji_id_mapping)

    @bot.event
    async def on_reaction_add(reaction, user):
        await handle_reaction(bot, reaction, user, contributors, emoji_id_mapping)