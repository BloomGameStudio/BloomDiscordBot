"""
proposal_modal is a discord.ui.Modal that is used to create or edit a proposal. It is used in the ProposalButtonsView class.
"""

import discord
from discord import ui
from proposals.proposals import proposals
from consts.types import GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE
from typing import Dict, Any


class ProposalModal(ui.Modal, title="Create/Edit Proposal"):
    name = ui.TextInput(
        label="Proposal title:", style=discord.TextStyle.short, required=True
    )

    proposal_type = ui.TextInput(
        label="Proposal type:", style=discord.TextStyle.short, required=True
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

    def __init__(self, channel, proposal):
        super().__init__()
        self.channel = channel
        self.proposal = proposal

        if proposal is not None:
            self.name.default = proposal["title"]
            self.proposal_type.default = proposal["type"]
            self.background.default = proposal["background"]
            self.abstract.default = proposal["abstract"]
            self.additional.default = proposal["additional"]

    async def on_submit(self, interaction: discord.Interaction) -> None:
        member_id: int = interaction.user.id

        # Check if the proposal type is valid
        if self.proposal_type.value not in [GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE]:
            await interaction.response.send_message(
                'Invalid proposal type. It must be either "governance" or "budget".',
                ephemeral=True,
            )
            return

        # Check if a proposal with the same name already exists
        if any(proposal["title"] == self.name.value for proposal in proposals):
            await interaction.response.send_message(
                'A proposal with this name already exists.',
                ephemeral=True,
            )
            return

        if self.proposal is None:
            new_proposal: Dict[str, Any] = {
                "member_id": member_id,
                "title": self.name.value,
                "type": self.proposal_type.value,
                "abstract": self.abstract.value,
                "background": self.background.value,
                "additional": self.additional.value,
            }
            # Add the created proposal to the global proposals list
            proposals.append(new_proposal)
        else:
            self.proposal["title"] = self.name.value
            self.proposal["type"] = self.proposal_type.value
            self.proposal["abstract"] = self.abstract.value
            self.proposal["background"] = self.background.value
            self.proposal["additiona"] = self.additional.value

        # Clear the buttons and show the response when a proposal is created/edited
        e = discord.Embed()
        e.title = f"Thank you, proposal has been created/edited. Use the same command again to edit or delete an existing proposal"
        e.description = f"{self.name.value}"
        e.set_author(
            name="Proposal Creation/Editing",
            icon_url=interaction.user.display_avatar.url,
        )
        e.color = discord.Color.green()
        await interaction.response.edit_message(content=" ", embed=e, view=None)
        