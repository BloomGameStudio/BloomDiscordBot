from discord.ext import commands
from events.command_operations import list_events_operation, delete_event_operation

"""
When the bot is initiated the command list below will be loaded so that they can be called.
The function calls related to the commands are located in command_operations.py

setup_event_commands is used so that all event commands can be loaded at once. instead of individually.
"""

def setup_event_commands(bot: commands.Bot):
    @bot.command(name='list_events')
    async def list_events(ctx):
        guild = ctx.guild
        formatted_string = await list_events_operation(guild)
        await ctx.send(f"🗓️ **All Events**🗓️ \n\n{formatted_string}")

    @bot.command(name='delete_event')
    async def delete_event(ctx, event_id: int = None):
        if event_id is None:
            await ctx.send("Please enter an event_id with this command. Example: `$deleteevent 1179241076016566272`")
            return

        guild = ctx.guild

        try:
            event_id = int(event_id)
        except ValueError:
            await ctx.send("Invalid event_id. Please provide a valid integer. Use $listevents to get a list of events")
            return

        message = await delete_event_operation(guild, event_id)
        await ctx.send(message)

    @bot.command(name='bot_help')
    async def help_command(ctx):
        help_message = (
            "**Here are the available commands this bot supports:**\n\n"
            "```\n"
            "$list_events: List all upcoming events.\n"
            "```\n"
            "$delete_event [event_id]: Delete an event with the specified ID.\n"
            "```\n"
            "$contributors: List all stored contributors, Name, UID.\n"
            "```\n"
            "$add_contributor: Allows you to add a contributor to stored contributors\n"
            "  you provide the following after the bot responds: name, UID, EmojiID\n"
            "```\n"
            "$remove_contributor: Allows you to remove a contributor; you must provide a contributor's UID with this command\n"
            "```\n"
            "$publish_draft: Allows you to publish a draft and start a vote coutdown."
            "```\n"
            "$v or $vote_draft: Allows you to start drafting a proposal. These can be edited by using the same command and reacting with 📝"
            "```\n"
            "$bot_help: This will give you the list of commands available.\n"
            "```\n"
            "This bot will also DM contributors if you react to a message with their respective emoji, or include it in a message"
        )

        await ctx.send(help_message)