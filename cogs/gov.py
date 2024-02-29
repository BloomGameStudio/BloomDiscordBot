import discord
from discord.ext import commands
from discord import app_commands
from proposals.proposal_buttons_view import ProposalButtonsView
from proposals.proposal_selects import PublishDraftSelect
from proposals.proposals import proposals


class GovCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vote_draft")
    async def vote_draft(self, interaction: discord.Interaction) -> None:
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

    @app_commands.command(name="publish_draft")
    async def publish_draft(self, interaction: discord.Interaction) -> None:
        """
        Publish an existing draft proposal.

        Parameters:
        interaction (discord.Interaction): The interaction of the command invocation.
        """
        try:
            view = discord.ui.View()
            view.add_item(PublishDraftSelect(proposals, self.bot))
            await interaction.response.send_message("Select a proposal.", view=view)
        except Exception as e:
            await interaction.response.send_message("Couldn't access proposal data.")
