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
from controllers.appearance_manager import *
from controllers.command_manager import *
from controllers.data_manager import *
from controllers.settings import *

class Bot:
    def __init__(self):
        self.bot = None
        self.contributors = None
        self.emoji_dicts = None
        self.data = None

        self.__command_manager = CommandManager()
        self.__appearance_manager = AppearanceManager()
        self.__data_manager = DataManager()
        self.__settings = Settings()
        self.__bot_user = None

    async def __refresh_name(self):
        await self.__appearance_manager.refresh_title_state(self, self.__data_manager, self.__bot_user, self.__settings)
        new_momentum = self.__data_manager.token_manager.bitcoin.price_momentum
        if not self.__settings.momentum == new_momentum:
            self.__settings.update_momentum(new_momentum)

    async def __refresh_status(self):
        await self.__appearance_manager.refresh_status(self, self.__data_manager, self.__bot_user, self.__settings)

    def load_data(self):
        with open(CONTRIBUTORS_FILE_PATH, "r") as json_file:
            self.data = json.load(json_file)
            self.contributors = {
                "priv-server": self.data["servers"]["priv-server"]["contributors"],
                "pub-server": self.data["servers"]["pub-server"]["contributors"],
            }
            self.emoji_dicts = {
                "priv-server": self.data["servers"]["priv-server"]["emoji_dictionary"],
                "pub-server": self.data["servers"]["pub-server"]["emoji_dictionary"],
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
        setup_shared_events(self.bot, self.__command_manager, self.__data_manager, self.__settings, self.data, proposals, new_proposal_emoji)
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