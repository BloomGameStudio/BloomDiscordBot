from logger.logger import logger
from discord.ext import tasks

@tasks.loop(minutes=5)
async def ongoing_proposals_checker():
    try:
        pass
    except Exception as e:
        logger.error(f"An error occurred while checking ongoing proposals: {e}")
