"""
ProposalButtonsView is a discord.ui.View that contains buttons for creating, editing, and deleting proposals. It is used in the vote_draft command in the GovCommandsCog class.
"""

import discord
from .proposal_modal import ProposalModal
from .proposal_selects import DeleteProposalSelect, EditProposalSelect, PreviewProposalSelect


class ProposalButtonsView(discord.ui.View):
    def __init__(self, proposals):
        super().__init__()
        self.proposals = proposals

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Create a new ProposalModal
        modal = ProposalModal(interaction.channel, None)
        # Send the modal as a response to the interaction
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.blurple)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.proposals:
            await interaction.response.send_message("No proposals to edit.")
        else:
            self.clear_items()
            self.add_item(EditProposalSelect(self.proposals))
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if there are any proposals to delete
        if not self.proposals:
            await interaction.response.send_message("No proposals to delete.")
        else:
            self.clear_items()
            self.add_item(DeleteProposalSelect(self.proposals))
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Preview", style=discord.ButtonStyle.grey)
    async def preview(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if there are any proposals to preview
        if not self.proposals:
            await interaction.response.send_message("No proposals to edit.")
        else:
            self.clear_items()
            self.add_item(PreviewProposalSelect(self.proposals))
            await interaction.response.edit_message(view=self)