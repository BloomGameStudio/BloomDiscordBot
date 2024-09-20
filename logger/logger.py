import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)
handler.setFormatter(formatter)

logger.addHandler(handler)

if __name__ == "__main__":
    try:
        x = 1 / 0
    except Exception as e:
        logger.error("A division by zero occurred: %s", e)
