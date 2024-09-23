"""
proposal_selects is a discord.ui.select that contains the select menus for the publish_draft, delete_draft, and edit_draft commands. It is used in the vote_draft command in the GovCommandsCog class.
"""

import discord
from proposals.proposals import ProposalManager
from .proposal_modal import FirstProposalModal


class PublishDraftSelect(discord.ui.Select):
    def __init__(self, proposals, bot):
        self.proposals = proposals
        self.bot = bot
        options = [
            discord.SelectOption(label=proposal["title"], value=proposal["title"])
            for proposal in self.proposals
        ]
        super().__init__(placeholder="Select a proposal to publish", options=options)

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

        await ProposalManager.handle_publish_draft(
            interaction, selected_proposal["title"], self.proposals, self.bot
        )


class DeleteProposalSelect(discord.ui.Select):
    def __init__(self, proposals, bot):
        self.proposals = proposals
        self.bot = bot
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
    def __init__(self, proposals, bot):
        self.proposals = proposals
        self.bot = bot
        options = [
            discord.SelectOption(label=proposal["title"], value=proposal["title"])
            for proposal in self.proposals
        ]
        super().__init__(placeholder="Select a proposal to edit", options=options)

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

        if not hasattr(self.bot, "proposal_data"):
            self.bot.proposal_data = {}

        self.bot.proposal_data[interaction.user.id] = selected_proposal.copy()

        modal = FirstProposalModal(self.bot, interaction.channel, selected_proposal)
        await interaction.response.send_modal(modal)


class PreviewProposalSelect(discord.ui.Select):
    def __init__(self, proposals, bot):
        self.proposals = proposals
        self.bot = bot
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

        content = (
            f"**Bloom {proposal_type} Proposal:** {selected_proposal['title']}\n\n"
            f"**Authors:** {selected_proposal['authors']}\n\n"
            f"**Abstract:**\n{selected_proposal['abstract']}\n\n"
            f"**Definitions:**\n{selected_proposal['definitions']}\n\n"
            f"**Background:**\n{selected_proposal['background']}\n\n"
        )

        if selected_proposal.get("implementation"):
            content += f"**Implementation Protocol:**\n{selected_proposal['implementation']}\n\n"

        if selected_proposal.get("voting_choices"):
            content += f"**Voting Choices:**\n{selected_proposal['voting_choices']}\n\n"

        await interaction.followup.send(content, ephemeral=True)

        await interaction.followup.send(
            "**Preview complete.** Use the /vote_draft command again to edit, preview or delete an existing proposal.",
            ephemeral=True,
        )
