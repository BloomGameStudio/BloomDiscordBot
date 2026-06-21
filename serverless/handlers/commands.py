"""
Command Handlers

Each handler processes a specific Discord slash command.
Returns an InteractionResponse with the result.
"""

import json
from typing import Dict, Any, Optional
from serverless.utils.interaction_response import InteractionResponse, InteractionResponseType, create_embed


class CommandHandler:
    """Base class for command handlers."""

    async def handle(self, interaction: Dict[str, Any]) -> InteractionResponse:
        """Process the interaction and return response."""
        raise NotImplementedError


class HelpCommandHandler(CommandHandler):
    """Handles /help command - returns list of available commands."""

    async def handle(self, interaction: Dict[str, Any]) -> InteractionResponse:
        """Return help message with all available commands."""
        help_text = """
__ 🌺 **Bloom Bot Commands** 🌺 __
Commands can be prompted with **/

**/help**
Display this help message with all available commands.

**/add_contributor {member} {emoji}**
Add a new member (and associated emoji) to the list of core contributors.

**/remove_contributor {member}**
Remove an existing member from the list of core contributors.

**/contributors**
Return a list of core contributors.

**/list_events**
Return a list of upcoming events.

**/create_proposal {thread_id}**
Create a new proposal from a draft thread and submit it for voting.
Use the thread ID from your draft proposal URL.
"""

        return InteractionResponse(
            response_type=InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            content=help_text,
        )


class ContributorsCommandHandler(CommandHandler):
    """Handles /contributors command - returns list of contributors."""

    def __init__(self, db_service):
        """
        Initialize with database service.

        Args:
            db_service: Database service for fetching contributors
        """
        self.db = db_service

    async def handle(self, interaction: Dict[str, Any]) -> InteractionResponse:
        """Return list of contributors."""
        try:
            guild_id = interaction["guild_id"]

            # Fetch contributors from database
            contributors = self.db.get_contributors(guild_id)

            if not contributors:
                return InteractionResponse(
                    content="No contributors found for this server.",
                )

            # Format the response
            contributor_lines = []
            for contrib in contributors:
                emoji = contrib.get("emoji", "")
                name = contrib.get("name", "Unknown")
                contributor_lines.append(f"{emoji} {name}")

            content = "**Bloom Contributors**\n" + "\n".join(contributor_lines)

            return InteractionResponse(
                response_type=InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                content=content,
            )

        except Exception as e:
            return InteractionResponse(
                content=f"Error fetching contributors: {str(e)}",
                ephemeral=True,
            )


class AddContributorCommandHandler(CommandHandler):
    """Handles /add_contributor command."""

    def __init__(self, db_service):
        self.db = db_service

    async def handle(self, interaction: Dict[str, Any]) -> InteractionResponse:
        """Add a contributor to the database."""
        try:
            # Extract command options
            options = interaction.get("data", {}).get("options", [])
            member_id = None
            emoji = None

            for option in options:
                if option["name"] == "member":
                    member_id = option["value"]
                elif option["name"] == "emoji":
                    emoji = option["value"]

            if not member_id or not emoji:
                return InteractionResponse(
                    content="Missing required parameters: member and emoji",
                    ephemeral=True,
                )

            guild_id = interaction["guild_id"]
            user_id = interaction["member"]["user"]["id"]

            # TODO: Check if user has permission to add contributors
            # For now, allow all users

            # Add to database
            self.db.add_contributor(guild_id, member_id, emoji)

            return InteractionResponse(
                content=f"Contributor added successfully! {emoji}",
            )

        except Exception as e:
            return InteractionResponse(
                content=f"Error adding contributor: {str(e)}",
                ephemeral=True,
            )


# Command handler registry
COMMAND_HANDLERS = {
    "help": HelpCommandHandler(),
    # "contributors": ContributorsCommandHandler(db_service),  # Will be injected
    # "add_contributor": AddContributorCommandHandler(db_service),
    # "remove_contributor": RemoveContributorCommandHandler(db_service),
    # "list_events": ListEventsCommandHandler(db_service),
    # "create_proposal": CreateProposalCommandHandler(db_service, bot_service),
}


def get_command_handler(command_name: str) -> Optional[CommandHandler]:
    """Get the handler for a command."""
    return COMMAND_HANDLERS.get(command_name)
