"""
ProposalButtonsView is a discord.ui.View that contains buttons for creating, editing, and deleting proposals. It is used in the vote_draft command in the GovCommandsCog class.
"""


import discord
from .proposal_modal import FirstProposalModal
from .proposal_selects import (
    DeleteProposalSelect,
    EditProposalSelect,
    PreviewProposalSelect,
)


class ProposalButtonsView(discord.ui.View):
    def __init__(self, proposals, bot):
        super().__init__()
        self.proposals = proposals
        self.bot = bot

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)
    async def create_proposal(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        view = discord.ui.View()
        view.add_item(CreateGeneralProposalButton(self.proposals, self.bot))
        view.add_item(CreateBudgetProposalButton(self.proposals, self.bot))

        await interaction.response.send_message(
            content="Select Proposal Type:", view=view, ephemeral=True
        )

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.blurple)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.proposals:
            await interaction.response.send_message(
                "No proposals to edit.", ephemeral=True
            )
        else:
            self.clear_items()
            self.add_item(EditProposalSelect(self.proposals, self.bot))
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Preview", style=discord.ButtonStyle.grey)
    async def preview(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not self.proposals:
            await interaction.response.send_message(
                "No proposals to preview.", ephemeral=True
            )
        else:
            self.clear_items()
            self.add_item(PreviewProposalSelect(self.proposals, self.bot))
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.proposals:
            await interaction.response.send_message(
                "No proposals to delete.", ephemeral=True
            )
        else:
            self.clear_items()
            self.add_item(DeleteProposalSelect(self.proposals, self.bot))
            await interaction.response.edit_message(view=self)


class CreateGeneralProposalButton(discord.ui.Button):
    def __init__(self, proposals, bot):
        super().__init__(label="General", style=discord.ButtonStyle.green)
        self.proposals = proposals
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        modal = FirstProposalModal(
            self.bot, interaction.channel, proposal_type="governance"
        )
        await interaction.response.send_modal(modal)


class CreateBudgetProposalButton(discord.ui.Button):
    def __init__(self, proposals, bot):
        super().__init__(label="Budget", style=discord.ButtonStyle.green)
        self.proposals = proposals
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        modal = FirstProposalModal(
            self.bot, interaction.channel, proposal_type="budget"
        )
        await interaction.response.send_modal(modal)
