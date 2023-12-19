import discord
import os
from discord.ext import commands
from bot.commands import setup_commands
from bot.events import setup_events
from updates.updates import load_posted_events

def main():
    # Discord Config
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    bot = commands.Bot(command_prefix="$", intents=intents)

    # Setup commands and events
    setup_commands(bot)
    setup_events(bot)

    load_posted_events()

    # Run the bot
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    main()
