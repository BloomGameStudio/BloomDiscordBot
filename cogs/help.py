"""
HelpCommandCog class is a cog that contains the help command for the bot.
It contains the following command:
- help: List all available commands that the bot can perform.
"""

import discord
from discord.ext import commands
from discord import app_commands
from consts.constants import MENU_COPY


class HelpCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help")
    async def help_commands(self, interaction: discord.Interaction):
        """
        Lis1t all available commands that the bot can perform.
        """
        await interaction.response.send_message(MENU_COPY)
