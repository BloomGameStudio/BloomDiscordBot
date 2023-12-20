import discord
from discord.ext import commands
from emotes.commands import setup_contrbitutor_commands
from emotes.events import setup_contributor_events
from constants import DISCORD_BOT_TOKEN

def main():
    # Discord Config
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    bot = commands.Bot(command_prefix="$", intents=intents)

    # Setup the emotes discord commands, and events
    setup_contrbitutor_commands(bot)
    setup_contributor_events(bot)

    # Run the bot
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()