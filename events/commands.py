"""
When the bot is initiated the command list below will be loaded so that they can be invoked.
The function calls related to the commands are located in command_operations.py

setup_event_commands is used so that all event commands can be loaded at once. instead of individually.
"""
import discord
from discord.ext import commands
from discord.ext.commands import Context
from events.command_operations import list_events_operation, delete_event_operation


async def setup_event_commands(bot: commands.Bot) -> None:
    """
    Setup the event-related commands.

    Parameters:
    bot (commands.Bot): The bot instance.
    """
    @bot.tree.command()
    async def list_events(interaction: discord.Interaction):
        """
        List all the events in the guild. list_events_operation from command_operations.py is invoked.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        """
        guild = interaction.guild
        formatted_string = await list_events_operation(guild)
        await interaction.response.send_message(f"🗓️ **All Events**🗓️ \n\n{formatted_string}")
    
    await bot.tree.delete_command('delete_event')

    @bot.tree.command(name="delete_event")
    async def delete_event(interaction: discord.Interaction, event_name: str = None):
        """
        Deletes an event in the guild. delete_event_operation from command_operations.py is invoked.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        event_name (str): The name of the event to be deleted.

        """
        if event_name is None:
            await interaction.response.send_message(
                "Please enter an event name with this command. Example: `/delete_event My Event`"
            )
            return

        guild = interaction.guild

        message = await delete_event_operation(interaction, guild, event_name)
        await interaction.response.send_message(message)