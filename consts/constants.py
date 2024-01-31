# Valid ids and keys that can be selected to be incremented or in rare cases decremented in the config.ini file
# Any other value should raise an error
CONFIG_ID_MAP: dict[str, str] = {"governance": "governance_id", "budget": "budget_id"}
CONFIG_ABSOLUTE_PATH = "config/config.ini"
