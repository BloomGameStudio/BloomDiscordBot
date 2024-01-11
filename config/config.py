import configparser
import logging

# Load configuration
config = configparser.ConfigParser()
config.read('config/config.ini')  

current_governance_id = config.getint('ID_START_VALUES', 'governance_id')
current_budget_id = config.getint('ID_START_VALUES', 'budget_id')

# Set up logging
logging_level = config.get('Logging', 'level', fallback='INFO')
numeric_logging_level = getattr(logging, logging_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_logging_level)

# Update values when proposals are submitted.
def update_id_values(id_value, id_type):
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    if id_type.lower() == 'governance':
        config['ID_START_VALUES']['governance_id'] = str(id_value)
    elif id_type.lower() == 'budget':
        config['ID_START_VALUES']['budget_id'] = str(id_value)

    with open('config/config.ini', 'w') as configfile:
        config.write(configfile)
