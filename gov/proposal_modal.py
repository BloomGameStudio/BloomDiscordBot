import discord
from discord import ui
from discord import Embed
from .proposals import proposals
from .command_operations import handle_publishdraft
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
        label="Proposal abstract:", style=discord.TextStyle.paragraph, required=True
    )

    background = ui.TextInput(
        label="Proposal background:", style=discord.TextStyle.paragraph, required=True
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

    async def on_submit(self, interaction: discord.Interaction) -> None:
        member_id: int = interaction.user.id

        # Check if the proposal type is valid
        if self.proposal_type.value not in [GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE]:
            await interaction.response.send_message(
                'Invalid proposal type. It must be either "governance" or "budget".',
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
            }
            # Add the created proposal to the global proposals list
            proposals.append(new_proposal)
        else:
            self.proposal["title"] = self.name.value
            self.proposal["type"] = self.proposal_type.value
            self.proposal["abstract"] = self.abstract.value
            self.proposal["background"] = self.background.value

        e = Embed()
        e.title = f"Thank you, proposal has been created/edited. Use the same command again to edit or delete an existing proposal"
        e.description = f"{self.name.value}"
        await interaction.response.send_message(embed=e)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
