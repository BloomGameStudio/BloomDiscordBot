import discord
import os
from discord.ext import commands
from events.commands import setup_event_commands
from events.events import setup_event_events
from events.event_operations import load_posted_events
from gov.commands import setup_gov_commands
from gov.events import setup_gov_events

def main():
    # Discord Config
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    bot = commands.Bot(command_prefix="$", intents=intents)
    bot.posted_events = load_posted_events()

    # Setup the event discord commands, and events
    setup_event_commands(bot)
    setup_event_events(bot)
    
    # Setup the governance discord commands, and events
    setup_gov_commands(bot)
    setup_gov_events(bot)

    # Run the bot
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == "__main__":
    main()