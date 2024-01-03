import discord
import os
import json
from discord.ext import commands
from gov.commands import setup_gov_commands
from emotes.commands import setup_contrbitutor_commands
from shared.constants import CONTRIBUTORS_FILE_PATH, new_proposal_emoji
from shared.event_operations import handle_message, handle_reaction
from gov.proposals import proposals

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

    # Setup the shared message event handling
    def setup_events(bot: commands.Bot, contributors, emoji_id_mapping, proposals):
        @bot.event
        async def on_message(message):
            await handle_message(bot, message, contributors, emoji_id_mapping, proposals)

    def setup_reaction_events(bot: commands.Bot, contributors, emoji_id_mapping, proposals, new_proposal_emoji):
        @bot.event
        async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
            await handle_reaction(bot, reaction, user, contributors, emoji_id_mapping, proposals, new_proposal_emoji)

    # Call the setup functions
    setup_events(bot, contributors, emoji_id_mapping, proposals)
    setup_reaction_events(bot, contributors, emoji_id_mapping, proposals, new_proposal_emoji)

    # Run the bot
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == "__main__":
    main()