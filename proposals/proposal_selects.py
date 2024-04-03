"""
proposal_selects is a discord.ui.select that contains the select menus for the publish_draft, delete_draft, and edit_draft commands. It is used in the vote_draft command in the GovCommandsCog class.
"""

import discord
from proposals.proposals import handle_publishdraft
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

class PreviewProposalSelect(discord.ui.Select):
    def __init__(self, proposals):
        self.proposals = proposals
        options = [
            discord.SelectOption(label=proposal["title"], value=proposal["title"])
            for proposal in self.proposals
        ]
        super().__init__(placeholder="Select a proposal to preview", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Find the selected proposal
        for proposal in self.proposals:
            if proposal["title"] == self.values[0]:
                selected_proposal = proposal
                break
        else:
            await interaction.response.send_message("Proposal not found.")
            return

        # Send proposal attributes as individual messages
        await interaction.response.send_message(f'{selected_proposal["title"]}')
        await interaction.followup.send(f'{selected_proposal["background"]}')
        await interaction.followup.send(f'{selected_proposal["abstract"]}')

        # Check if additional information is present
        if selected_proposal["additional"]:
            await interaction.followup.send(f'{selected_proposal["additional"]}')
        await interaction.followup.send("Preview complete. Use the /vote_draft command again to edit or delete an existing proposal.")