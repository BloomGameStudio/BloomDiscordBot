import discord
from discord import ui
from proposals.proposals import ProposalManager


class FirstProposalModal(ui.Modal):
    def __init__(self, bot, channel, proposal=None, proposal_type=None):
        super().__init__(title="Create/Edit Proposal - Step 1")
        self.bot = bot
        self.channel = channel
        self.proposal = proposal
        self.proposal_type = proposal_type or (
            proposal.get("type") if proposal else None
        )

        self.name = ui.TextInput(
            label="Proposal Title",
            style=discord.TextStyle.short,
            required=True,
            max_length=100,
        )
        self.authors = ui.TextInput(
            label="Proposal Authors",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500,
        )
        self.abstract = ui.TextInput(
            label="Proposal Abstract",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000,
        )
        self.definitions = ui.TextInput(
            label="Proposal Definitions",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000,
        )

        self.add_item(self.name)
        self.add_item(self.authors)
        self.add_item(self.abstract)
        self.add_item(self.definitions)

        if proposal:
            self.name.default = proposal["title"]
            self.authors.default = proposal.get("authors", "")
            self.abstract.default = proposal["abstract"]
            self.definitions.default = proposal.get("definitions", "")

    def generate_full_title(self, proposal_type, draft_title):
        """
        Generate the full title of the proposal with the prefix based on the proposal type.

        Parameters:
        proposal_type (str): The type of proposal.
        draft_title (str): The title of the proposal.

        Returns:
        str: The full title of the proposal
        """
        if proposal_type == "governance":
            prefix = "Bloom General Proposal: "
        elif proposal_type == "budget":
            prefix = "Bloom Budget Proposal: "
        else:
            prefix = ""
        return prefix + draft_title

    async def on_submit(self, interaction: discord.Interaction):
        proposal_data = {
            "member_id": interaction.user.id,
            "title": self.name.value,
            "authors": self.authors.value,
            "abstract": self.abstract.value,
            "definitions": self.definitions.value,
            "type": self.proposal_type,
        }

        full_title = self.generate_full_title(
            proposal_data["type"], proposal_data["title"]
        )
        if len(full_title) > 100:
            await interaction.response.send_message(
                "The total length of the proposal title including prefix exceeds 100 characters. Please shorten your title.",
                ephemeral=True,
            )
            return

        if not hasattr(self.bot, "proposal_data"):
            self.bot.proposal_data = {}

        self.bot.proposal_data[interaction.user.id] = proposal_data

        view = ProceedToSecondModalView(self.bot, self.proposal)
        await interaction.response.send_message(
            "Please click the button below to proceed to the next step.",
            view=view,
            ephemeral=True,
        )


class ProceedToSecondModalView(discord.ui.View):
    def __init__(self, bot, proposal=None):
        super().__init__()
        self.bot = bot
        self.proposal = proposal

    @discord.ui.button(label="Proceed to Step 2", style=discord.ButtonStyle.primary)
    async def proceed_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        user_id = interaction.user.id
        proposal_data = self.bot.proposal_data.get(user_id)
        if proposal_data is None:
            await interaction.response.send_message(
                "No proposal data found. Please start over.", ephemeral=True
            )
            return

        second_modal = SecondProposalModal(self.bot, proposal_data, self.proposal)
        await interaction.response.send_modal(second_modal)


class SecondProposalModal(ui.Modal):
    def __init__(self, bot, proposal_data, proposal=None):
        super().__init__(title="Create/Edit Proposal - Step 2")
        self.bot = bot
        self.proposal_data = proposal_data
        self.proposal = proposal

        self.background = ui.TextInput(
            label="Proposal Background",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000,
        )
        self.implementation = ui.TextInput(
            label="Implementation Protocol",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000,
        )
        # self.voting_choices = ui.TextInput(
        #    label="Voting Choices",
        #    style=discord.TextStyle.paragraph,
        #    required=False,
        #    max_length=500,
        # )

        self.add_item(self.background)
        self.add_item(self.implementation)
        # self.add_item(self.voting_choices)

        self.background.default = self.proposal_data.get("background", "")
        self.implementation.default = self.proposal_data.get("implementation", "")
        # self.voting_choices.default = self.proposal_data.get("voting_choices", "")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            self.proposal_data.update(
                {
                    "background": self.background.value,
                    "implementation": self.implementation.value,
                    # "voting_choices": self.voting_choices.value,
                }
            )

            full_title = FirstProposalModal.generate_full_title(
                self, self.proposal_data["type"], self.proposal_data["title"]
            )
            if len(full_title) > 100:
                await interaction.response.send_message(
                    "The total length of the proposal title including prefix exceeds 100 characters. Please shorten your title.",
                    ephemeral=True,
                )
                return

            if self.proposal is None and any(
                proposal["title"] == self.proposal_data["title"]
                for proposal in ProposalManager.proposals
            ):
                await interaction.response.send_message(
                    "A proposal with this title already exists.",
                    ephemeral=True,
                )
                return

            if self.proposal is None:
                ProposalManager.proposals.append(self.proposal_data)
            else:
                self.proposal.update(self.proposal_data)

            e = discord.Embed()
            e.title = "Thank you, your proposal has been created/edited."
            e.description = f"{self.proposal_data['title']}"
            e.set_author(
                name="Proposal Creation/Editing",
                icon_url=interaction.user.display_avatar.url,
            )
            e.color = discord.Color.green()

            await interaction.response.send_message(embed=e, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                f"Something went wrong. Error: {str(e)}", ephemeral=True
            )
