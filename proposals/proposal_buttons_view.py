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

    @discord.ui.button(label="Create Proposal", style=discord.ButtonStyle.green)
    async def create_proposal(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        self.add_item(CreateGeneralProposalButton(self.proposals))
        self.add_item(CreateBudgetProposalButton(self.proposals))
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Edit Proposal", style=discord.ButtonStyle.blurple)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.proposals:
            await interaction.response.send_message(
                "No proposals to edit.", ephemeral=True
            )
        else:
            self.clear_items()
            self.add_item(EditProposalSelect(self.proposals))
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Preview Proposal", style=discord.ButtonStyle.grey)
    async def preview(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.proposals:
            await interaction.response.send_message("No proposals to preview.", ephemeral=True)
        else:
            self.clear_items()
            self.add_item(PreviewProposalSelect(self.proposals))
            await interaction.response.edit_message(view=self)
            await interaction.response.send_message(view=self)

    @discord.ui.button(label="Delete Proposal", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.proposals:
            await interaction.response.send_message(
                "No proposals to delete.", ephemeral=True
            )
        else:
            self.clear_items()
            self.add_item(DeleteProposalSelect(self.proposals))
            await interaction.response.edit_message(view=self)


class CreateGeneralProposalButton(discord.ui.Button):
    def __init__(self, proposals):
        super().__init__(label="General Proposal", style=discord.ButtonStyle.green)
        self.proposals = proposals

    async def callback(self, interaction: discord.Interaction):
        modal = ProposalModal(interaction.channel, None, proposal_type="governance")
        await interaction.response.send_modal(modal)


class CreateBudgetProposalButton(discord.ui.Button):
    def __init__(self, proposals):
        super().__init__(label="Budget Proposal", style=discord.ButtonStyle.green)
        self.proposals = proposals

    async def callback(self, interaction: discord.Interaction):
        modal = ProposalModal(interaction.channel, None, proposal_type="budget")
        await interaction.response.send_modal(modal)
