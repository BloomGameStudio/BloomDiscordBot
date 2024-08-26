import os
import configparser
from logger.logger import logger

# Map of proposal types to their respective ID keys in the config file
CONFIG_ID_MAP: dict[str, str] = {"governance": "governance_id", "budget": "budget_id"}
CONFIG_ABSOLUTE_PATH = "config/config.ini"

# File paths for JSON files containing information about contributors and posted events IDs
CONTRIBUTORS_FILE_PATH = "./data/contributors.json"
POSTED_EVENTS_FILE_PATH = "./data/posted_events.json"
ONGOING_VOTES_FILE_PATH = "./data/ongoing_votes.json"

# Load configuration
config: configparser.ConfigParser = configparser.ConfigParser()
config.read(CONFIG_ABSOLUTE_PATH)

# Determine the environment
ENV = os.getenv("ENV", "dev").lower()  # Default to 'dev' if ENV is not set

# Load ID values
current_governance_id: int = config.getint("ID_START_VALUES", "governance_id")
current_budget_id: int = config.getint("ID_START_VALUES", "budget_id")

# Load environment-specific settings
SNAPSHOT_SPACE = config.get(ENV, "SNAPSHOT_SPACE")
DISCORD_VOTE_ENDTIME = config.getint(ENV, "DISCORD_VOTE_ENDTIME")
YES_COUNT_THRESHOLD = config.getint(ENV, "DISCORD_YES_COUNT_THRESHOLD")
SNAPSHOT_URL_PREFIX = config.get(ENV, "SNAPSHOT_URL_PREFIX")
SNAPSHOT_HUB = config.get(ENV, "SNAPSHOT_HUB")
NETWORK_ID = config.get(ENV, "NETWORK_ID")
PRIMARY_RPC_URL = config.get(ENV, "PRIMARY_RPC_URL")
SECONDARY_RPC_URL = config.get(ENV, "SECONDARY_RPC_URL")
SETTINGS_NAME = config.get(ENV, "SETTINGS_NAME")
SETTINGS_ABOUT = config.get(ENV, "SETTINGS_ABOUT")
SETTINGS_SYMBOL = config.get(ENV, "SETTINGS_SYMBOL")
SETTINGS_MEMBERS = config.get(ENV, "SETTINGS_MEMBERS").split(',')
SETTINGS_STRATEGIES = config.get(ENV, "SETTINGS_STRATEGIES")

def increment_config_id(
    id_type: str, increment: int = +1, config: configparser.ConfigParser = config
) -> None:
    """
    Increments the ID value for a given proposal type in the config file.

    Note: Use typed id_types instead of using raw strings these can be imported from consts

    Args:
      id_type: A string specifying the ID type ('governance' or 'budget')
      increment: An integer specifying how much to increment the ID by (default 1)
      config: A ConfigParser instance (default uses config initialized here)

    Returns:
        None
    """

    id_type = id_type.lower()

    if id_type not in CONFIG_ID_MAP:
        err_msg = f"Invalid id_type: {id_type}"
        logger.error(err_msg)
        raise ValueError(err_msg)

    key = CONFIG_ID_MAP[id_type]
    new_value = int(config["ID_START_VALUES"][key]) + increment
    config["ID_START_VALUES"][key] = str(new_value)

    try:
        with open(CONFIG_ABSOLUTE_PATH, "w") as f:
            config.write(f)

    except IOError as e:
        err_msg = f"Error writing config file: {e}"
        logger.error(err_msg)
        raise Exception(err_msg, e)
