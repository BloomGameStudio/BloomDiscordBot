"""
The GovCommandsCog class is a cog that contains the commands for the governance commands.
It contains the following commands:
- vote_draft: Draft, edit, or delete a vote proposal.
- publish_draft: Publish an existing draft proposal.

"""


import discord
from discord.ext import commands
from discord import app_commands
from proposals.proposal_buttons_view import ProposalButtonsView
from proposals.proposal_selects import PublishDraftSelect
from proposals.proposals import ProposalManager
from discord.ext import commands
from discord import app_commands
from proposals.thread_parser import ThreadParser
from utils.utils import Utils
import logging

logger = logging.getLogger(__name__)

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
            view = ProposalButtonsView(ProposalManager.proposals)
            await interaction.response.send_message(
                "Click create to create a new proposal, edit, or delete to modify an existing proposal.",
                view=view,
                ephemeral=True,
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
            view.add_item(PublishDraftSelect(ProposalManager.proposals, self.bot))
            await interaction.response.send_message(
                "Select a proposal.", view=view, ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                "Couldn't access proposal data.", ephemeral=True
            )

    @app_commands.command(
        name="create_proposal",
        description="Create a proposal from an existing thread"
    )
    @app_commands.describe(
        thread_id="The thread ID or URL to create a proposal from"
    )
    async def create_proposal(
        self, 
        interaction: discord.Interaction, 
        thread_id: str
    ) -> None:
        """Create a proposal from a thread and start voting"""
        try:
            await interaction.response.defer()
            
            # Parse the thread content
            try:
                thread_data = await ThreadParser.parse_thread(self.bot, thread_id)
            except ValueError as e:
                await interaction.followup.send(f"Error: {str(e)}")
                return
            
            if not thread_data:
                await interaction.followup.send("Failed to parse thread content")
                return

            # Create draft format for ProposalManager with separate messages
            draft = {
                "member_id": str(interaction.user.id),
                "title": thread_data["title"],
                "type": thread_data["type"],
                "sections": thread_data["sections"]
            }

            success = await ProposalManager.publish_draft(
                draft,
                self.bot,
                interaction.guild_id,
                interaction.guild
            )

            if success:
                await interaction.followup.send("Proposal created successfully!")
            else:
                await interaction.followup.send("Failed to create proposal")

        except Exception as e:
            logger.error(f"Error creating proposal: {e}")
            await interaction.followup.send("An error occurred while creating the proposal")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GovCommandsCog(bot))
