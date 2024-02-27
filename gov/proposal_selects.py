import discord
from .command_operations import handle_publishdraft
from .proposal_modal import ProposalModal


class PublishDraftSelect(discord.ui.Select):
    def __init__(self, proposals, bot):
        self.proposals = proposals
        self.bot = bot
        options = [
            discord.SelectOption(label=proposal["title"], value=proposal["title"])
            for proposal in self.proposals
        ]
        super().__init__(placeholder="proposals..", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Find the selected proposal
        for proposal in self.proposals:
            if proposal["title"] == self.values[0]:
                selected_proposal = proposal
                break
        else:
            await interaction.response.send_message("Proposal not found.")
            return

        # Call handle_publishdraft
        await handle_publishdraft(
            interaction, selected_proposal["title"], self.proposals, self.bot
        )


class DeleteProposalSelect(discord.ui.Select):
    def __init__(self, proposals):
        self.proposals = proposals
        options = [
            discord.SelectOption(label=proposal["title"], value=proposal["title"])
            for proposal in self.proposals
        ]
        super().__init__(placeholder="Select a proposal to delete", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Find the selected proposal
        for index, proposal in enumerate(self.proposals):
            if proposal["title"] == self.values[0]:
                selected_proposal = proposal
                del self.proposals[index]  # Delete the selected proposal from the list
                e = discord.Embed(
                    title=f'Proposal "{selected_proposal["title"]}" has been deleted',
                    color=discord.Color.red(),
                )
                e.set_author(
                    name="Proposal Deletion",
                    icon_url=interaction.user.display_avatar.url,
                )
                await interaction.response.edit_message(content=" ", embed=e, view=None)
                return

        await interaction.response.send_message("Proposal not found.")


class EditProposalSelect(discord.ui.Select):
    def __init__(self, proposals):
        self.proposals = proposals
        options = [
            discord.SelectOption(label=proposal["title"], value=proposal["title"])
            for proposal in self.proposals
        ]
        super().__init__(placeholder="Select a proposal to edit", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Find the selected proposal
        for proposal in self.proposals:
            if proposal["title"] == self.values[0]:
                selected_proposal = proposal
                break
        else:
            await interaction.response.send_message("Proposal not found.")
            return

        # Open the ProposalModal with the selected proposal
        modal = ProposalModal(interaction.channel, selected_proposal)
        await interaction.response.send_modal(modal)
