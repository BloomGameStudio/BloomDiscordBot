import discord
from discord import ui
from discord import Embed

proposals = []

class Proposal:
    def __init__(self, member_id, title, proposal_type, abstract, background):
        self.member_id = member_id
        self.title = title
        self.proposal_type = proposal_type
        self.abstract = abstract
        self.background = background

class ProposalModal(ui.Modal, title="Create/Edit Proposal"):
    proposal = None
    channel = None

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
            self.name.default = proposal.title
            self.proposal_type.default = proposal.proposal_type
            self.background.default = proposal.background
            self.abstract.default = proposal.abstract

    async def on_submit(self, interaction: discord.Interaction):
        member_id = interaction.user.id

        if self.proposal is None:
            self.proposal = Proposal(
                member_id=member_id,
                title=self.name.value,
                proposal_type=self.proposal_type.value,
                abstract=self.abstract.value,
                background=self.background.value
            )
            # Add the created proposal to the global proposals list
            proposals.append(self.proposal)
        else:
            self.proposal.title = self.name.value
            self.proposal.proposal_type = self.proposal_type.value
            self.proposal.abstract = self.abstract.value
            self.proposal.background = self.background.value

        e = Embed()
        e.title = f"Thank you, proposal has been created/edited."
        e.description = f"{self.proposal.title}"
        e.footer.text = 'Use the buttons under this embed to publish this draft or edit it.'
        await interaction.response.send_message(embed=e, view=ProposalButtonsView(proposals))

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

class ProposalSelect(discord.ui.Select):
    def __init__(self, proposals, placeholder="Select a proposal to edit"):
        self.proposals = proposals if proposals is not None else []
        if not self.proposals:
            options = [discord.SelectOption(label="No proposals to select", value="No proposals")]
        else:
            options = [discord.SelectOption(label=proposal.title, value=proposal.title) for proposal in self.proposals]
        super().__init__(placeholder=placeholder, options=options)

    async def on_select(self, interaction: discord.Interaction, option: discord.SelectOption):
        # Defer the interaction
        await interaction.response.defer()

        # Find the selected proposal
        for proposal in self.proposals:
            if proposal.title == option.value:
                selected_proposal = proposal
                break
        else:
            await interaction.followup.send('Proposal not found.')
            return

        # Create a new ProposalModal with the selected proposal
        try:
            modal = ProposalModal(interaction.channel, selected_proposal)
        except Exception as e:
            raise e

        # Send the modal as a response to the interaction
        try:
            await interaction.followup.send_modal(modal)
        except Exception as e:
            raise e
        
class ProposalButtonsView(discord.ui.View):
    def __init__(self, proposals):
        super().__init__()
        self.proposals = proposals
        self.add_item(ProposalSelect(proposals, placeholder="Select a proposal to delete"))

    @discord.ui.button(label='Create', style=discord.ButtonStyle.green)
    async def publish(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Create a new ProposalModal
        modal = ProposalModal(interaction.channel, None)
        # Send the modal as a response to the interaction
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Edit', style=discord.ButtonStyle.blurple)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.proposals:
            await interaction.response.send_message('No proposals to edit.')
        else:
            self.clear_items()
            self.add_item(ProposalSelect(self.proposals, placeholder="Select a proposal to edit"))
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.proposals:
            await interaction.response.send_message('No proposals to delete.')
        else:
            # Get the selected proposal's title
            selected_proposal_title = self.children[0].value

            # Remove the selected proposal from the global proposals list
            proposals[:] = [p for p in proposals if p.title != selected_proposal_title]

            # Clear the items from the view and add the updated ProposalSelect dropdown
            self.clear_items()
            self.add_item(ProposalSelect(proposals, placeholder="Select a proposal to delete"))

            await interaction.response.edit_message(view=self)