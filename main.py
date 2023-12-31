import discord
import os
import json
from discord.ext import commands
from gov.commands import setup_gov_commands
from gov.proposals import proposals
from emotes.commands import setup_contrbitutor_commands
from events.commands import setup_event_commands
from events.events import setup_event_events
from events.event_operations import load_posted_events
from shared.constants import CONTRIBUTORS_FILE_PATH, new_proposal_emoji
from shared.events import setup_shared_events

def main():
    # Load contributors and emoji ID mapping from contributors.json
    with open(CONTRIBUTORS_FILE_PATH, 'r') as json_file:
        data = json.load(json_file)
        contributors = data["contributors"]
        emoji_id_mapping = {emoji: contributor for emoji, contributor in data["emojiIdMapping"].items()}

    # Discord Config
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    bot = commands.Bot(command_prefix="$", intents=intents)
    
    # Setup the governance discord commands, and events
    setup_gov_commands(bot)
    
    # Setup the emotes discord commands, and events
    setup_contrbitutor_commands(bot, contributors, emoji_id_mapping)

    # Setup the shared events
    setup_shared_events(bot, contributors, emoji_id_mapping, proposals, new_proposal_emoji)
    bot.posted_events = load_posted_events()

    # Setup the event discord commands, and events
    setup_event_commands(bot)
    setup_event_events(bot)

    # Run the bot
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == "__main__":
    main()