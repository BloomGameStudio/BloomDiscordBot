from updates.updates import check_upcoming_events
from discord.ext import commands

def setup_commands(bot: commands.Bot):
    @bot.command(name='list_events')
    async def listevents(ctx):
        guild = ctx.guild
        event_list = await check_upcoming_events(guild)

        # Extracting event information
        event_info_list = [(event.name, event.id, event.description) for event in event_list]

        # Formatting the information
        formatted_events = [
            f"🌺 **{name}**🌺 \n**event_id: **{event_id}\n**Description:** {description}"
            for name, event_id, description in event_info_list
        ]
        formatted_string = "\n\n".join(formatted_events)

        await ctx.send(f"🗓️ **All Events**🗓️ \n\n{formatted_string}")

    @bot.command(name='delete_event')
    async def deleteevent(ctx, event_id: int = None):
        if event_id is None:
            await ctx.send("Please enter an event_id with this command. Example: `$deleteevent 1179241076016566272`")
            return

        guild = ctx.guild

        try:
            event_id = int(event_id)
        except ValueError:
            await ctx.send("Invalid event_id. Please provide a valid integer. Use $listevents to get a list of events")
            return

        event = guild.get_scheduled_event(event_id)

        if event:
            # Delete the event
            await event.delete()
            await ctx.send(f"Event with ID {event_id} has been deleted 🗑️")
        else:
            await ctx.send(f"No event found with ID {event_id}.")

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