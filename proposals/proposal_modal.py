"""
proposal_modal is a discord.ui.Modal that is used to create or edit a proposal. It is used in the ProposalButtonsView class.
"""

import discord
from discord import ui
from proposals.proposals import proposals


class ProposalModal(ui.Modal, title="Create/Edit Proposal"):
    name = ui.TextInput(
        label="Proposal title:", style=discord.TextStyle.short, required=True
    )

    abstract = ui.TextInput(
        label="Proposal Authors & Abstract:",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000,
    )

    background = ui.TextInput(
        label="Proposal Definitions & Background:",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000,
    )

    additional = ui.TextInput(
        label="Implementation Protocol & Voting Choices:",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=2000,
    )

    def __init__(self, channel, proposal, proposal_type=None):
        super().__init__()
        self.channel = channel
        self.proposal = proposal
        self.proposal_type = (
            proposal.get("type") if proposal is not None else proposal_type
        )

        if proposal is not None:
            self.name.default = proposal["title"]
            self.background.default = proposal["background"]
            self.abstract.default = proposal["abstract"]
            self.additional.default = proposal["additional"]

    def generate_full_title(self, proposal_type, draft_title):
        if proposal_type == "governance":
            prefix = f"Bloom General Proposal: "
        elif proposal_type == "budget":
            prefix = f"Bloom Budget Proposal: "
        else:
            prefix = ""

        return prefix + draft_title

    async def on_submit(self, interaction: discord.Interaction) -> None:
        member_id: int = interaction.user.id

        full_title = self.generate_full_title(self.proposal_type, self.name.value)
        if len(full_title) > 100:
            await interaction.response.send_message(
                "The total length of the proposal title including prefix exceeds 100 characters. Please shorten your title.",
                ephemeral=True,
            )
            return

        if self.proposal is None and any(
            proposal["title"] == self.name.value for proposal in proposals
        ):
            await interaction.response.send_message(
                "A proposal with this name already exists.",
                ephemeral=True,
            )
            return

        proposal_data = {
            "member_id": member_id,
            "title": self.name.value,
            "type": self.proposal_type,
            "abstract": self.abstract.value,
            "background": self.background.value,
            "additional": self.additional.value,
        }

        if self.proposal is None:
            proposals.append(proposal_data)
        else:
            self.proposal.update(proposal_data)

        e = discord.Embed()
        e.title = f"Thank you, proposal has been created/edited. Use the same command to edit the proposal."
        e.description = f"{self.name.value}"
        e.set_author(
            name="Proposal Creation/Editing",
            icon_url=interaction.user.display_avatar.url,
        )
        e.color = discord.Color.green()
        await interaction.response.edit_message(content=" ", embed=e, view=None)
