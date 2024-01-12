import discord
from discord import ui
from domain.proposal import Proposal
import traceback
from discord import Embed

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
        # Creation case...
        if self.proposal is None:
            self.proposal = await Proposal.create(
                member_id=member_id,
                title=self.name,
                proposal_type=self.proposal_type,
                abstract=self.abstract,
                background=self.background
            )
        else:
            # else if we passed an existing proposal to the modal...
            # we are instead editing an existing proposal
            await Proposal.filter(id=self.proposal.id).update (
                title = self.name,
                proposal_type = self.proposal_type,
                abstract = self.abstract,
                background = self.background
            )
            self.proposal = await Proposal.filter(id=self.proposal.id).first()
        e = Embed()
        e.title = f"Thank you, proposal {self.proposal.id} has been created/edited."
        e.description = f"{self.proposal}"
        e.footer.text = 'Use the buttons under this embed to publish this draft or edit it.'
        await interaction.response.send_message(embed=e, view=ProposalButtonsView(self.proposal))
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)
    
class ProposalButtonsView(discord.ui.View):
    proposal = None
    
    def __init__(self, proposal):
        super().__init__()
        self.proposal = proposal

    @discord.ui.button(label='Publish', style=discord.ButtonStyle.green)
    async def publish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=self, content="Button not functional yet.")

    @discord.ui.button(label='Edit', style=discord.ButtonStyle.blurple)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ProposalModal(interaction.channel, self.proposal)) 

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=self, content="Button not functional yet.")
