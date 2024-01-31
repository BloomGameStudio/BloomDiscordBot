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
from shared.events import setup_shared_events
from shared.constants import CONTRIBUTORS_FILE_PATH, new_proposal_emoji


class Bot:
    def __init__(self):
        self.bot = None
        self.contributors = None
        self.emoji_dicts = None
        self.data = None

    def load_data(self):
        with open(CONTRIBUTORS_FILE_PATH, "r") as json_file:
            self.data = json.load(json_file)
            self.contributors = {
                "Bloom Studio": self.data["servers"]["Bloom Studio"]["contributors"],
                "Bloom Collective": self.data["servers"]["Bloom Collective"][
                    "contributors"
                ],
            }
            self.emoji_dicts = {
                "Bloom Studio": self.data["servers"]["Bloom Studio"][
                    "emoji_dictionary"
                ],
                "Bloom Collective": self.data["servers"]["Bloom Collective"][
                    "emoji_dictionary"
                ],
            }

    def setup_bot(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

    def setup_commands_and_events(self):
        setup_gov_commands(self.bot)
        setup_contrbitutor_commands(self.bot, self.contributors, self.emoji_dicts)
        setup_shared_events(self.bot, self.data, proposals, new_proposal_emoji)
        self.bot.posted_events = load_posted_events()
        setup_event_commands(self.bot)
        setup_event_events(self.bot)

    def run(self):
        self.bot.run(os.getenv("DISCORD_BOT_TOKEN"))

    def main(self):
        self.load_data()
        self.setup_bot()
        self.setup_commands_and_events()
        self.run()


if __name__ == "__main__":
    runner = Bot()
    runner.main()
