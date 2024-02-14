"""
When the bot is initiated the command list below will be loaded so that they can be invoked.
The function calls related to the commands are located in command_operations.py

setup_contributor_commands is used so that all event commands can be loaded at once. instead of individually.
"""

import discord
from typing import List, Dict
from discord.ext import commands
from emotes.command_operations import (
    list_contributors,
    remove_contributor,
    add_contributor,
)


def setup_contrbitutor_commands(
    bot: commands.Bot,
    contributors: Dict[str, List[Dict[str, str]]],
    emoji_dicts: Dict[str, Dict[str, str]],
) -> None:
    """
    Setup the contributor-related commands for the bot.

    Parameters:
    bot (commands.Bot): The bot to add commands to.
    contributors (Dict[str, List[Dict[str, str]]]): The contributors to manage.
    emoji_dicts (Dict[str, Dict[str, str]]): The emojis to use in the commands.
    """

    @bot.tree.command(name="contributors")
    async def listcontributors(interaction: discord.Interaction) -> None:
        """
        Invokes list_contributors which lists all the contributors in a specific guild/s.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        """
        await list_contributors(interaction, contributors, emoji_dicts)

    @bot.tree.command(name="remove_contributor")
    async def removecontributor(interaction: discord.Interaction, user_mention: str) -> None:
        """
        Invokes remove_contributor which removes a contributor if applicable contributor exists
        and the user invoking the command has the authorization to do so.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        user_mention (str): The mention of the user to remove.
        """
        await remove_contributor(interaction, contributors, emoji_dicts, user_mention)

    @bot.tree.command(name="add_contributor")
    async def addcontributor(interaction: discord.Interaction, user_mention: str, emoji: str) -> None:
        """
        Invokes add_contributor which adds a contributor,
        if the user invoking the command has the authorization to do so.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        user_mention (str): The mention of the user to be added as a contributor.
        emoji (str): The emoji associated with the user.
        """
        await add_contributor(interaction, user_mention, emoji, contributors, emoji_dicts, bot)
