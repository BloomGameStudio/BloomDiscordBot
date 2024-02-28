import configparser
from logger.logger import logger

# Map of proposal types to their respective ID keys in the config file
CONFIG_ID_MAP: dict[str, str] = {"governance": "governance_id", "budget": "budget_id"}
CONFIG_ABSOLUTE_PATH = "config/config.ini"

# File paths for JSON files containing information about contributors and posted events IDs
CONTRIBUTORS_FILE_PATH = "./config/contributors.json"
POSTED_EVENTS_FILE_PATH = "./config/posted_events.json"


# Load configuration
config: configparser.ConfigParser = configparser.ConfigParser()
config.read("config/config.ini")

current_governance_id: int = config.getint("ID_START_VALUES", "governance_id")
current_budget_id: int = config.getint("ID_START_VALUES", "budget_id")


# Update values when proposals are submitted.
def update_id_values(id_value: int, id_type: str) -> None:
    config = configparser.ConfigParser()
    config.read("config/config.ini")

    if id_type.lower() == "governance":
        config["ID_START_VALUES"]["governance_id"] = str(id_value)
    elif id_type.lower() == "budget":
        config["ID_START_VALUES"]["budget_id"] = str(id_value)

    with open("config/config.ini", "w") as configfile:
        config.write(configfile)


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
    config["ID_START_VALUES"][key] += str(increment)

    try:
        with open(CONFIG_ABSOLUTE_PATH, "w") as f:
            config.write(f)

    except IOError as e:
        err_msg = f"Error writing config file: {e}"
        logger.error(err_msg)
        raise Exception(err_msg, e)
