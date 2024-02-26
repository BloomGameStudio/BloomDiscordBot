import discord
from discord.ext import commands
from discord import app_commands
from consts.constants import MENU_COPY
from logger.logger import logger

class HelpCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help")
    async def help_commands(self, interaction: discord.Interaction):
        """
        Lis1t all available commands that the bot can perform.
        """
        logger.info("Command fired")
        await interaction.response.send_message(MENU_COPY)

def setup(bot: commands.Bot):
    bot.add_cog(HelpCommandCog(bot))