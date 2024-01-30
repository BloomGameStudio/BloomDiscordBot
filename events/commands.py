from discord.ext import commands
from discord.ext.commands import Context
from events.command_operations import list_events_operation, delete_event_operation

"""
When the bot is initiated the command list below will be loaded so that they can be called.
The function calls related to the commands are located in command_operations.py

setup_event_commands is used so that all event commands can be loaded at once. instead of individually.
"""


def setup_event_commands(bot: commands.Bot) -> None:
    @bot.command(name="list_events")
    async def list_events(ctx: Context) -> None:
        guild = ctx.guild
        formatted_string = await list_events_operation(guild)
        await ctx.send(f"🗓️ **All Events**🗓️ \n\n{formatted_string}")

    @bot.command(name="delete_event")
    async def delete_event(ctx: Context, event_id: int = None) -> None:
        if event_id is None:
            await ctx.send(
                "Please enter an event_id with this command. Example: `$deleteevent 1179241076016566272`"
            )
            return

        guild = ctx.guild

        try:
            event_id = int(event_id)
        except ValueError:
            await ctx.send(
                "Invalid event_id. Please provide a valid integer. Use $listevents to get a list of events"
            )
            return

        message = await delete_event_operation(guild, event_id)
        await ctx.send(message)
