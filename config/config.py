import os
import configparser
from logger.logger import logger

CONFIG_ABSOLUTE_PATH = "config/config.ini"

config: configparser.ConfigParser = configparser.ConfigParser()
config.read(CONFIG_ABSOLUTE_PATH)

ENV = os.getenv("ENV", "DEV")

SNAPSHOT_SPACE = config.get(ENV, "SNAPSHOT_SPACE")
DISCORD_VOTE_ENDTIME = config.getint(ENV, "DISCORD_VOTE_ENDTIME")
YES_COUNT_THRESHOLD = config.getint(ENV, "DISCORD_YES_COUNT_THRESHOLD")
SNAPSHOT_URL_PREFIX = config.get(ENV, "SNAPSHOT_URL_PREFIX")
SNAPSHOT_HUB = config.get(ENV, "SNAPSHOT_HUB")
NETWORK_ID = config.get(ENV, "NETWORK_ID")
SETTINGS_NAME = config.get(ENV, "SETTINGS_NAME")
SETTINGS_ABOUT = config.get(ENV, "SETTINGS_ABOUT")
SETTINGS_SYMBOL = config.get(ENV, "SETTINGS_SYMBOL")
SETTINGS_MEMBERS = config.get(ENV, "SETTINGS_MEMBERS").split(",")
SETTINGS_ADMINS = config.get(ENV, "SETTINGS_ADMINS").split(",")
SETTINGS_STRATEGIES = config.get(ENV, "SETTINGS_STRATEGIES")
SETTINGS_TOKEN_ADDRESSES = config.get(ENV, "SETTINGS_TOKEN_ADDRESSES").split(",")

PRIMARY_RPC_URL = os.getenv("PRIMARY_RPC_URL")
SECONDARY_RPC_URL = os.getenv("SECONDARY_RPC_URL")
