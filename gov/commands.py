"""
When the bot is initiated the command list below will be loaded so that they can be called.
The function invocations related to the commands are located in gov/command_operations.py

setup_gov_commands is used so that all event commands can be loaded at once. instead of individually.
"""

from discord.ext import commands
from .command_operations import handle_votedraft, handle_publishdraft
from .proposals import proposals
from consts.constants import new_proposal_emoji


def setup_gov_commands(bot: commands.Bot) -> None:
    """
    Set up the governance commands for the bot.

    Parameters:
    bot (commands.Bot): The bot instance.
    """

    @bot.command(name="vote_draft", aliases=["v"], pass_context=True)
    async def votedraft(ctx):
        """
        Handle the vote draft command. This command allows you to start drafting a vote.

        Parameters:
        ctx (commands.Context): The context in which the command was called.
        """
        await handle_votedraft(ctx, proposals, new_proposal_emoji)

    @bot.command(name="publish_draft")
    async def publishdraft(ctx: commands.Context, *, draft_name: str) -> None:
        """
        Handle the publish draft command. This command verifies the draft exists
        before invoking publish_draft in command_operations.py.

        Parameters:
        ctx (commands.Context): The context in which the command was called.
        draft_name (str): The name of the draft to be published.
        """
        if not draft_name:
            await ctx.send("Please provide a draft name.")
            return
        await handle_publishdraft(ctx, draft_name, proposals, bot)
