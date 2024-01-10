import configparser
import logging
from typing import Any

# Load configuration
config: configparser.ConfigParser = configparser.ConfigParser()
config.read('config/config.ini')  

current_governance_id: int = config.getint('ID_START_VALUES', 'governance_id')
current_budget_id : int = config.getint('ID_START_VALUES', 'budget_id')

# Set up logging
logging_level: str = config.get('Logging', 'level', fallback='INFO')
numeric_logging_level: int = getattr(logging, logging_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_logging_level)

# Update values when proposals are submitted.
def update_id_values(id_value: int, id_type: str) -> None:
    config = configparser.ConfigParser()
    config.read('config/config.ini')  # Corrected path

    if id_type.lower() == 'governance':
        config['ID_START_VALUES']['governance_id'] = str(id_value)
    elif id_type.lower() == 'budget':
        config['ID_START_VALUES']['budget_id'] = str(id_value)

    with open('config/config.ini', 'w') as configfile:  # Corrected path
        config.write(configfile)