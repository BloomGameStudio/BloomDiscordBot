from discord.ext import commands
from discord.ext.commands import Context
from events.command_operations import list_events_operation, delete_event_operation

"""
When the bot is initiated the command list below will be loaded so that they can be invoked.
The function calls related to the commands are located in command_operations.py

setup_event_commands is used so that all event commands can be loaded at once. instead of individually.
"""


def setup_event_commands(bot: commands.Bot) -> None:
    """
    Setup the event-related commands.

    Parameters:
    bot (commands.Bot): The bot instance.
    """

    @bot.command(name="list_events")
    async def list_events(ctx: Context) -> None:
        """
        List all the events in the guild. list_events_operation from command_operations.py is invoked.

        Parameters:
        ctx (Context): The context of the command invocation.
        """
        guild = ctx.guild
        formatted_string = await list_events_operation(guild)
        await ctx.send(f"🗓️ **All Events**🗓️ \n\n{formatted_string}")

    @bot.command(name="delete_event")
    async def delete_event(ctx: Context, event_id: int = None) -> None:
        """
        Deletes an event in the guild. delete_event_operation from command_operations.py is invoked.

        Parameters:
        ctx (Context): The context of the command invocation.
        event_id (int): The ID of the event to be deleted.

        """
        if event_id is None:
            await ctx.send(
                "Please enter an event_id with this command. Example: `!delete_event 1179241076016566272`"
            )
            return

        guild = ctx.guild

        try:
            event_id = int(event_id)
        except ValueError:
            await ctx.send(
                "Invalid event_id. Please provide a valid ID. Use !list_events to get a list of events"
            )
            return

        message = await delete_event_operation(ctx, guild, event_id)
        await ctx.send(message)
