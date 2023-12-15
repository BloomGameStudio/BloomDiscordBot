import discord
import os
import asyncio
from discord.ext import commands, tasks
from emojis.emojis import emoji_id_mapping, contributors, send_dm_once, update_json_file, add_contributor
from updates.updates import check_upcoming_events, load_dotenv, notify_new_event, format_event, load_posted_events, save_posted_events, get_guild_scheduled_event_users
from gov.proposals import proposals, new_proposal_emoji, publish_draft, get_governance_id, textwrap, get_budget_id
from shared.shared import logging

#Load ENV
load_dotenv()

#Discord Config
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="$", intents=intents)

#Bot events
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="Watching you sleep"))

    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emojis'))
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        await check_upcoming_events(guild)
        # Start the background task to check events automatically every 24 hours
        daily_check_events.start()
    else:
        logging.error("Discord server ID not found")

@bot.event
async def on_scheduled_event_create(event):
    logging.info(f"New scheduled event created: {event.name}")
    await notify_new_event(bot, event)

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
        "```\n"
        "$delete_event [event_id]: Delete an event with the specified ID.\n"
        "```\n"
        "```\n"
        "$contributors: List all stored contributors, Name, UID.\n"
        "```\n"
        "```\n"
        "$add_contributor: Allows you to add a contributor to stored contributors\n"
        "  you provide the following after the bot responds: name, UID, EmojiID\n"
        "```\n"
        "```\n"
        "$remove_contributor: Allows you to remove a contributor; you must provide a contributor's UID with this command\n"
        "```\n"
        "```\n"
        "$publish_draft: Allows you to publish a draft and start a vote coutdown."
        "```\n"
        "```\n"
        "$v or $vote_draft: Ällows you to start drafting a proposal. These can be edited by using the same command and reacting with 📝"
        "```\n"
        "```\n"
        "$bot_help: This will give you the list of commands available.\n"
        "```\n"
        "This bot will also DM contributors if you react to a message with their respective emoji, or include it in a message"
    )

    await ctx.send(help_message)

#Bot tasks
@tasks.loop(minutes=59)
async def daily_check_events():
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        event_list = await check_upcoming_events(guild, time_range=24 * 3600)

        if not event_list:
            logging.info("No upcoming events in the next 24 hours.")
            return

        channel_id = int(os.getenv("GENERAL_CHANNEL_ID"))
        channel = guild.get_channel(channel_id)

        if not channel:
            logging.warning("Event channel not found")
            return

        # Common message part
        common_message = f"<:inevitable_bloom:1178256658741346344> **Upcoming Events in the Next 24 Hours** <:inevitable_bloom:1178256658741346344> \n"

        # Load posted events
        posted_events = load_posted_events()

        # Check if it's the initial run or not
        if not posted_events:
            # Initial run, post events to Discord
            for event in event_list:
                # Fetch subscribed users for each event
                users = get_guild_scheduled_event_users(guild_id, event.id)
                user_mentions = [f"<@{user['user_id']}>" for user in users]
                user_list_string = ', '.join(user_mentions)

                formatted_string = (
                    f"\n"
                    f"{common_message}\n"
                    f":link: **Event Link https://discord.com/events/{guild_id}/{event.id} :link:**\n"
                    f"\n"
                    f"{user_list_string}\n"
                )

                # Send message
                await channel.send(formatted_string)

            save_posted_events([event.id for event in event_list])
        else:
            # Subsequent runs, filter out already posted events
            new_events = [event for event in event_list if event.id not in posted_events]

            if new_events:
                for event in new_events:
                    # Fetch subscribed users for each event
                    users = get_guild_scheduled_event_users(guild_id, event.id)
                    user_mentions = [f"<@{user['user_id']}>" for user in users]
                    user_list_string = ', '.join(user_mentions)

                    formatted_string = (
                        f"{common_message}\n"
                        f":link: **Event Link https://discord.com/events/{guild_id}/{event.id} :link:**\n"
                        f"\n"
                        f"{user_list_string}\n"
                    )

                    # Send message
                    await channel.send(formatted_string)

                # Update the posted_events list only for newly posted events
                posted_events.extend([event.id for event in new_events])
                save_posted_events(posted_events)
            else:
                logging.info("No new upcoming events in the next 24 hours.")
    else:
        logging.warning("Guild not found")

bot.run(os.getenv('DISCORD_BOT_TOKEN'))