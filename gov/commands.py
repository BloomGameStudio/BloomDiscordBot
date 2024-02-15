from discord.ext import commands
from .proposals import proposals
from .proposal_buttons_view import ProposalButtonsView
from .proposal_selects import PublishDraftSelect
import discord


def setup_gov_commands(bot: commands.Bot) -> None:
    """
    Setup the government-related commands for the bot.

    Parameters:
    bot (commands.Bot): The bot to add commands to.
    """

    @bot.tree.command(name="vote_draft")
    async def votedraft(interaction: discord.Interaction) -> None:
        """
        Draft, edit, or delete a vote proposal

        Parameters:
        interaction (discord.Interaction): The interaction of the command invocation.
        """
        try:
            view = ProposalButtonsView(proposals)
            await interaction.response.send_message(
                "Click create to create a new proposal, edit, or delete to modify an existing proposal.",
                view=view,
            )
        except Exception as e:
            await interaction.response.send_message("Couldn't access proposal data.")

    @bot.tree.command(name="publish_draft")
    async def publishdraft(interaction: discord.Interaction) -> None:
        """
        Publish an existing draft proposal.

        Parameters:
        interaction (discord.Interaction): The interaction of the command invocation.
        """
        try:
            view = discord.ui.View()
            view.add_item(PublishDraftSelect(proposals, bot))
            await interaction.response.send_message("Select a proposal.", view=view)
        except Exception as e:
            await interaction.response.send_message("Couldn't access proposal data.")