import discord
from discord.ext import commands
from consts.constants import MENU_COPY


async def setup_shared_commands(bot: commands.Bot) -> None:
    @bot.tree.command(name="help")
    async def help_commands(interaction: discord.Interaction):
        """
        List all available commands that the bot can perform.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        """
        await interaction.response.send_message(MENU_COPY)
