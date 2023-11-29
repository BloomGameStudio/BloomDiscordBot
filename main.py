import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from updates import check_upcoming_events, format_event, notify_new_event

intents = discord.Intents.all()

load_dotenv()

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        await check_upcoming_events(guild)
        # Start the background task to check events automatically every 24 hours
        daily_check_events.start()
    else:
        print(f"Guild not found")

# This may have its own issues if the bot is restarted
@tasks.loop(hours=24)
async def daily_check_events():
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        event_list = await check_upcoming_events(guild, time_range=24 * 3600)

        if event_list:
            formatted_events = [format_event(event) for event in event_list]
            formatted_string = "\n\n".join(formatted_events)

            channel_id = int(os.getenv("CHANNEL_ID"))
            channel = guild.get_channel(channel_id)

            if channel:
                # Tag @here and send the message
                await channel.send(f"<:inevitable_bloom:1178256658741346344> **Upcoming Events in the Next 24 Hours - @here** <:inevitable_bloom:1178256658741346344> \n{formatted_string}")
            else:
                print(f"Event channel not found")
        else:
            print("No upcoming events in the next 24 hours.")
    else:
        print(f"Guild not found")

@bot.event
async def on_scheduled_event_create(event):
    print(f"New scheduled event created: {event.name}")
    await notify_new_event(bot, event)

@bot.command(name='listevents')
async def listevents(ctx):
    guild = ctx.guild
    event_list = await check_upcoming_events(guild)
    formatted_events = [format_event(event) for event in event_list]
    formatted_string = "\n\n".join(formatted_events)

    await ctx.send(f"🗓️**All Events**🗓️\n{formatted_string}")

@bot.command(name='deleteevent')
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

@bot.command(name='bothelp')
async def help_command(ctx):
    help_message = (
        "**Here are the available commands this bot supports:**\n\n"
        "```\n"
        "$listevents: List all upcoming events.\n"
        "```\n"
        "```\n"
        "$deleteevent [event_id]: Delete an event with the specified ID.\n"
        "```\n"
        "```\n"
        "$contributors: List all stored contributors, Name, UID.\n"
        "```\n"
        "```\n"
        "$addcontributor: Allows you to add a contributor to stored contributors\n"
        "  you provide the following after the bot responds: name, UID, EmojiID\n"
        "```\n"
        "```\n"
        "$removecontributor: Allows you to remove a contributor; you must provide a contributor's UID with this command\n"
        "```\n"
    )

    await ctx.send(help_message)

bot.run(os.getenv('TOKEN'))
