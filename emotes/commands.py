from discord.ext import commands
from emotes.command_operations import list_contributors, remove_contributor, add_contributor

"""
When the bot is initiated the command list below will be loaded so that they can be called.
The function calls related to the commands are located in command_operations.py

setup_contributor_commands is used so that all event commands can be loaded at once. instead of individually.
"""

def setup_contrbitutor_commands(bot: commands.Bot, contributors, emoji_id_mapping):
    @bot.command(name='contributors')
    async def listcontributors(ctx):
        await list_contributors(ctx, emoji_id_mapping)

    @bot.command(name='remove_contributor')
    async def removecontributor(ctx, user_mention=None):
        await remove_contributor(ctx, contributors, emoji_id_mapping, user_mention)
    
    @bot.command(name='add_contributor')
    async def addcontributor(ctx):
        await add_contributor(ctx, contributors, emoji_id_mapping, bot)