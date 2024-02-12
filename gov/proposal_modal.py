import discord
from discord import ui
from discord import Embed
from .proposals import proposals
from .command_operations import handle_publishdraft
from consts.types import GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE

class ProposalModal(ui.Modal, title="Create/Edit Proposal"):

    name = ui.TextInput(
        label='Proposal title:',
        style=discord.TextStyle.short,
        required=True
    )

    proposal_type = ui.TextInput(
        label='Proposal type:',
        style=discord.TextStyle.short,
        required=True
    )

    abstract = ui.TextInput(
        label='Proposal abstract:',
        style=discord.TextStyle.paragraph,
        required=True
    )

    background = ui.TextInput(
        label='Proposal background:',
        style=discord.TextStyle.paragraph,
        required=True
    )

    def __init__(self, channel, proposal):
        super().__init__()
        self.channel = channel
        self.proposal = proposal

        if proposal is not None:
            self.name.default = proposal['title']
            self.proposal_type.default = proposal['type']
            self.background.default = proposal['background']
            self.abstract.default = proposal['abstract']

    async def on_submit(self, interaction: discord.Interaction):
        member_id = interaction.user.id

        # Check if the proposal type is valid
        if self.proposal_type.value not in [GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE]:
            await interaction.response.send_message('Invalid proposal type. It must be either "governance" or "budget".', ephemeral=True)
            return

        if self.proposal is None:
            new_proposal = {
                'member_id': member_id,
                'title': self.name.value,
                'type': self.proposal_type.value,
                'abstract': self.abstract.value,
                'background': self.background.value
            }
            # Add the created proposal to the global proposals list
            proposals.append(new_proposal)
        else:
            self.proposal['title'] = self.name.value
            self.proposal['type'] = self.proposal_type.value
            self.proposal['abstract'] = self.abstract.value
            self.proposal['background'] = self.background.value

        e = Embed()
        e.title = f"Thank you, proposal has been created/edited. Use the same command again to edit or delete an existing proposal"
        e.description = f"{self.name.value}"
        await interaction.response.send_message(embed=e)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

class PublishDraftSelect(discord.ui.Select):
    def __init__(self, proposals, bot):
        self.proposals = proposals
        self.bot = bot
        options = [discord.SelectOption(label=proposal['title'], value=proposal['title']) for proposal in self.proposals]
        super().__init__(placeholder="Select a proposal to publish", options=options) 

    async def callback(self, interaction: discord.Interaction):
        # Find the selected proposal
        for proposal in self.proposals:
            if proposal['title'] == self.values[0]:
                selected_proposal = proposal
                break
        else:
            await interaction.response.send_message('Proposal not found.')
            return

        # Call handle_publishdraft
        await handle_publishdraft(interaction, selected_proposal['title'], self.proposals, self.bot)

class DeleteProposalSelect(discord.ui.Select):
    def __init__(self, proposals):
        self.proposals = proposals
        options = [discord.SelectOption(label=proposal.title, value=proposal.title) for proposal in self.proposals]
        super().__init__(placeholder="Select a proposal to delete", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Find the selected proposal
        for proposal in self.proposals:
            if proposal.title == self.values[0]:
                selected_proposal = proposal
                break
        else:
            await interaction.response.send_message('Proposal not found.')
            return

        # Remove the selected proposal from the proposals list
        self.proposals.remove(selected_proposal)
        await interaction.response.send_message(f'Proposal "{selected_proposal.title}" has been deleted.')

class EditProposalSelect(discord.ui.Select):
    def __init__(self, proposals):
        self.proposals = proposals
        options = [discord.SelectOption(label=proposal.title, value=proposal.title) for proposal in self.proposals]
        super().__init__(placeholder="Select a proposal to edit", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Find the selected proposal
        for proposal in self.proposals:
            if proposal.title == self.values[0]:
                selected_proposal = proposal
                break
        else:
            await interaction.response.send_message('Proposal not found.')
            return

        # Open the ProposalModal with the selected proposal
        modal = ProposalModal(interaction.channel, selected_proposal)
        await interaction.response.send_modal(modal)
                
class ProposalButtonsView(discord.ui.View):
    def __init__(self, proposals):
        super().__init__()
        self.proposals = proposals

    @discord.ui.button(label='Create', style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Create a new ProposalModal
        modal = ProposalModal(interaction.channel, None)
        # Send the modal as a response to the interaction
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if there are any proposals to delete
        if not self.proposals:
            await interaction.response.send_message('No proposals to delete.')
        else:
            self.clear_items()
            self.add_item(DeleteProposalSelect(self.proposals))
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label='Edit', style=discord.ButtonStyle.blurple)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.proposals:
            await interaction.response.send_message('No proposals to edit.')
        else:
            self.clear_items()
            self.add_item(EditProposalSelect(self.proposals))
            await interaction.response.edit_message(view=self)