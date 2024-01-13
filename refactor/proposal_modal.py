import discord
from discord import ui
from domain.proposal import Proposal
import traceback
from discord import Embed

"""
Proposal Modal is a CRUD interface for Proposal objects meant to be 
called from the discord interfaces. The proposal modal either takes
in a proposal object from the ORM domain or None (null). If there
is an object passed, it will treat it as an edit. If there is no 
object passed it will treat it as a creation. This spawns a message
upon completion and can be send in response to any interaction.
"""
class ProposalModal(ui.Modal, title="Create/Edit Proposal"):
    # The proposal object that is to be created or edited.
    proposal = None

    # The channel to show the altered/created object on completion.
    channel = None

    # Input field for title, title is a reserved word. Used "name"
    name = ui.TextInput(
        label='Proposal title:',
        style=discord.TextStyle.short,
        required=True
    )

    # input field for porposal type
    proposal_type = ui.TextInput(
        label='Proposal type:',
        style=discord.TextStyle.short,
        required=True
    )

    # input field for proposal abstract
    abstract = ui.TextInput(
        label='Proposal abstract:',
        style=discord.TextStyle.paragraph,
        required=True
    )

    # input field for background.
    background = ui.TextInput(
        label='Proposal background:',
        style=discord.TextStyle.paragraph,
        required=True
    )

    # constrcutor, create the base data.
    def __init__(self, channel, proposal):
        super().__init__()

        # Store channel and proposal as the modal's objects.
        self.channel = channel
        self.proposal = proposal

        # If the proposal isn't None, preload the data into the modal
        # This is the EDIT usecase.
        if proposal is not None:
            self.name.default = proposal.title
            self.proposal_type.default = proposal.proposal_type
            self.background.default = proposal.background
            self.abstract.default = proposal.abstract

    async def on_submit(self, interaction: discord.Interaction):
        # Get who did it.
        member_id = interaction.user.id

        # Creation case...
        if self.proposal is None:
            # No proposal existed before, we're making one... create DB obj.
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
            # assign the proposal back the the modal obj to update it.
            self.proposal = await Proposal.filter(id=self.proposal.id).first()
        
        # Grab the data an put it into an embed, attach the ProposalButtonsView
        e = Embed()
        e.title = f"Thank you, proposal {self.proposal.id} has been created/edited."
        e.description = f"{self.proposal}"
        e.footer.text = 'Use the buttons under this embed to publish this draft or edit it.'
        await interaction.response.send_message(embed=e, view=ProposalButtonsView(self.proposal))
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)

# ==================================================
# ==---HELPER VIEW CLASSES TO BE EXTERNALIZED-----==
# ==================================================
class ProposalButtonsView(discord.ui.View):
    proposal = None
    
    def __init__(self, proposal):
        super().__init__()
        self.proposal = proposal

    # A button to handle publishing
    @discord.ui.button(label='Publish', style=discord.ButtonStyle.green)
    async def publish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=self, content="Button not functional yet.")

    # A button to cause this modal to pop back up with the same data.
    @discord.ui.button(label='Edit', style=discord.ButtonStyle.blurple)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ProposalModal(interaction.channel, self.proposal)) 

    # A button letting you delete the proposal draft.
    @discord.ui.button(label='Delete', style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=self, content="Button not functional yet.")
