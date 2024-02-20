from logger.logger import logger
from .proposals import check_ongoing_proposals
from discord.ext import tasks, commands


@tasks.loop(minutes=5)
async def concluded_proposals_task(bot: commands.Bot):
    """
    This function is a task that runs every 5 minutes. It calls the check_ongoing_proposals function
    to check and process any proposals that have ended. If an error occurs during the execution of 
    check_ongoing_proposals, it logs the error.

    Parameters:
    bot (commands.Bot): The bot instance to pass to the check_ongoing_proposals function.

    Returns:
    None
    """
    try:
        await check_ongoing_proposals(bot)
    except Exception as e:
        logger.error(f"An error occurred while checking ongoing proposals: {e}")