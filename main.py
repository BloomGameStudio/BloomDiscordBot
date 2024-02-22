"""
The Bot class contains the bot's functionality. It has methods to load data from a JSON file, 
set up the bot with the necessary intents, set up commands and events, and runs the bot.

The JSON file located at emotes/contributors.json contains a list of contributors, and emoji_id => UID dictionaries
for two servers: 
"Bloom Studio" and "Bloom Collective". This data is loaded into the Bot instance when it's created.

The bot uses the following Discord Intents : message content, reactions, and members.

The bot has several commands and events, which are set up in the main method. 
These commands and events are defined in separate modules, which are imported at the tope of this code.
Refer to the specific files for more information.

"""

import discord
import os
import json
from discord.ext import commands
from gov.commands import setup_gov_commands
from gov.proposals import proposals
from emotes.commands import setup_contrbitutor_commands
from events.commands import setup_event_commands
from shared.commands import setup_shared_commands
from events.events import setup_event_events
from events.event_operations import load_posted_events
from config.config import CONTRIBUTORS_FILE_PATH, ONGOING_VOTES_FILE_PATH
from shared.events import setup_shared_events


class Bot:
    def main(self):

        try:
            with open(ONGOING_VOTES_FILE_PATH, "r") as json_file:
                try:
                    self.ongoing_votes = json.load(json_file)
                except json.JSONDecodeError:
                    self.ongoing_votes = {}
        except FileNotFoundError:
            self.ongoing_votes = {}

        # Load the contributor and dictionary data from the JSON file emotes/contributors.json
        with open(CONTRIBUTORS_FILE_PATH, "r") as json_file:
            self.data = json.load(json_file)
            self.contributors = {
                "Bloom Studio": self.data["servers"]["Bloom Studio"]["contributors"],
                "Bloom Collective": self.data["servers"]["Bloom Collective"][
                    "contributors"
                ],
            }
            self.emoji_dicts = {
                "Bloom Studio": self.data["servers"]["Bloom Studio"]["emoji_dictionary"],
                "Bloom Collective": self.data["servers"]["Bloom Collective"][
                    "emoji_dictionary"
                ],
            }

        # Setup the bot with intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        self.bot = commands.Bot(command_prefix="", intents=intents)

        self.bot.ongoing_votes = self.ongoing_votes
        self.bot.posted_events = load_posted_events()

        # Setup commands and events for the bot
        setup_gov_commands(self.bot)
        setup_contrbitutor_commands(self.bot, self.contributors, self.emoji_dicts)
        setup_shared_events(self.bot, self.data, proposals)
        setup_event_commands(self.bot)
        setup_event_events(self.bot)
        setup_shared_commands(self.bot)
        
        # Run the bot
        self.bot.run(os.getenv("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    # Create an instance of the bot and run main func
    Bot().main()
