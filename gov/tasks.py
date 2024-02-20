from logger.logger import logger
from .proposals import check_ongoing_proposals
from discord.ext import tasks, commands


@tasks.loop(minutes=5)
async def concluded_proposals_task(bot: commands.Bot):
    try:
        await check_ongoing_proposals(bot)
    except Exception as e:
        logger.error(f"An error occurred while checking ongoing proposals: {e}")