"""
proposal_selects is a discord.ui.select that contains the select menus for the publish_draft, delete_draft, and edit_draft commands. It is used in the vote_draft command in the GovCommandsCog class.
"""

import discord
from proposals.proposals import handle_publishdraft
from .proposal_modal import ProposalModal
from config import config as cfg


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
        for proposal in self.proposals:
            if proposal["title"] == self.values[0]:
                selected_proposal = proposal
                break
        else:
            await interaction.response.send_message("Proposal not found.")
            return

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
        for index, proposal in enumerate(self.proposals):
            if proposal["title"] == self.values[0]:
                selected_proposal = proposal
                del self.proposals[index]
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

        await interaction.response.send_message("Proposal not found.", ephemeral=True)


class EditProposalSelect(discord.ui.Select):
    def __init__(self, proposals):
        self.proposals = proposals
        options = [
            discord.SelectOption(label=proposal["title"], value=proposal["title"])
            for proposal in self.proposals
        ]
        super().__init__(placeholder="Select a proposal to edit", options=options)

    async def callback(self, interaction: discord.Interaction):
        for proposal in self.proposals:
            if proposal["title"] == self.values[0]:
                selected_proposal = proposal
                break
        else:
            await interaction.response.send_message(
                "Proposal not found.", ephemeral=True
            )
            return

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
        selected_proposal = next(
            (
                proposal
                for proposal in self.proposals
                if proposal["title"] == self.values[0]
            ),
            None,
        )

        if not selected_proposal:
            await interaction.response.send_message(
                "Proposal not found.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            "This is what your proposal will look like upon being published to Discord. The title will be the thread title:",
            ephemeral=True,
        )

        proposal_type = (
            "General" if selected_proposal["type"] == "governance" else "Budget"
        )

        await interaction.followup.send(
            f'Bloom {proposal_type} Proposal: {selected_proposal["title"]}',
            ephemeral=True,
        )

        await interaction.followup.send(
            f'{selected_proposal["abstract"]}', ephemeral=True
        )

        await interaction.followup.send(
            f'{selected_proposal["background"]}', ephemeral=True
        )

        if selected_proposal["additional"]:
            await interaction.followup.send(
                f'{selected_proposal["additional"]}', ephemeral=True
            )

        await interaction.followup.send(
            "**Preview complete.** Use the /vote_draft command again to edit, preview or delete an existing proposal.",
            ephemeral=True,
        )
