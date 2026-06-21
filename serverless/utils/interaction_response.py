"""
Discord Interaction Response Builder

Formats responses in the way Discord expects.
Handles different response types and interaction tokens.
"""

from typing import Optional, List, Dict, Any
from enum import Enum


class InteractionResponseType(Enum):
    """Discord interaction response types."""

    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class InteractionResponse:
    """Builder for Discord interaction responses."""

    def __init__(
        self,
        response_type: InteractionResponseType = InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        content: Optional[str] = None,
        ephemeral: bool = False,
    ):
        """
        Create an interaction response.

        Args:
            response_type: Type of response
            content: Message content
            ephemeral: Only visible to the user who invoked the command
        """
        self.response_type = response_type
        self.content = content
        self.ephemeral = ephemeral
        self.embeds: List[Dict[str, Any]] = []
        self.components: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to Discord API format."""
        data = {
            "type": self.response_type.value,
        }

        if self.response_type in [
            InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            InteractionResponseType.UPDATE_MESSAGE,
        ]:
            data["data"] = {
                "content": self.content or "",
                "flags": 64 if self.ephemeral else 0,  # 64 = ephemeral
            }

            if self.embeds:
                data["data"]["embeds"] = self.embeds

            if self.components:
                data["data"]["components"] = self.components

        elif self.response_type == InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE:
            data["data"] = {
                "flags": 64 if self.ephemeral else 0,
            }

        return data

    def add_embed(self, embed: Dict[str, Any]) -> "InteractionResponse":
        """Add an embed to the response."""
        self.embeds.append(embed)
        return self

    def add_component(self, component: Dict[str, Any]) -> "InteractionResponse":
        """Add a component (button, select, etc.) to the response."""
        self.components.append(component)
        return self


def create_embed(
    title: str,
    description: str,
    color: int = 0x7289DA,
    fields: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Create a Discord embed.

    Args:
        title: Embed title
        description: Embed description
        color: Embed color (RGB integer)
        fields: List of field dicts with 'name', 'value', 'inline'

    Returns:
        Embed dict for Discord API
    """
    embed = {
        "title": title,
        "description": description,
        "color": color,
    }

    if fields:
        embed["fields"] = fields

    return embed
