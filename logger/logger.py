import logging

# Create a logger
logger = logging.getLogger(__name__)

# Set the log level
logger.setLevel(logging.INFO)

# Define a Handler and set a format
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

if __name__ == "__main__":
    try:
        # Code that may raise an error
        x = 1 / 0
    except Exception as e:
        # Log the error
        logger.error("A division by zero occurred: %s", e)
