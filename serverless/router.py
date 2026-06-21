"""
Main Interaction Router

Receives interactions from Discord, validates them, and routes to appropriate handler.
"""

import json
import os
import logging
from typing import Dict, Any, Tuple
from serverless.utils.discord_validator import get_discord_validator
from serverless.utils.interaction_response import InteractionResponseType
from serverless.handlers.commands import get_command_handler


logger = logging.getLogger(__name__)


class InteractionRouter:
    """Routes Discord interactions to appropriate handlers."""

    def __init__(self, public_key: str):
        """
        Initialize router with Discord public key.

        Args:
            public_key: Discord app's PUBLIC_KEY from Developer Portal
        """
        self.validator = get_discord_validator(public_key)

    def validate_request(
        self, signature: str, timestamp: str, body: str
    ) -> bool:
        """Validate the request signature."""
        return self.validator.is_valid_request(signature, timestamp, body)

    def route(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route interaction to appropriate handler.

        Args:
            interaction: Discord interaction payload

        Returns:
            Response dict for Discord
        """
        interaction_type = interaction.get("type")

        # Handle PING (Discord checks if endpoint is valid)
        if interaction_type == 1:  # PING
            return {
                "type": InteractionResponseType.PONG.value,
            }

        # Handle slash commands
        if interaction_type == 2:  # APPLICATION_COMMAND
            return self._handle_command(interaction)

        # Unknown interaction type
        logger.warning(f"Unknown interaction type: {interaction_type}")
        return {
            "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            "data": {
                "content": "Unknown interaction type",
            },
        }

    def _handle_command(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle slash command interaction."""
        try:
            command_name = interaction.get("data", {}).get("name")

            if not command_name:
                logger.warning("Command name not found in interaction")
                return self._error_response("Invalid command")

            logger.info(f"Routing command: /{command_name}")

            # Get the handler
            handler = get_command_handler(command_name)

            if not handler:
                logger.warning(f"No handler found for command: {command_name}")
                return self._error_response(f"Command /{command_name} not found")

            # Handle the command (sync wrapper for async)
            import asyncio

            response = asyncio.run(handler.handle(interaction))

            return response.to_dict()

        except Exception as e:
            logger.error(f"Error handling command: {str(e)}", exc_info=True)
            return self._error_response(f"Error processing command: {str(e)}")

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            "data": {
                "content": message,
                "flags": 64,  # ephemeral
            },
        }


def create_router() -> InteractionRouter:
    """Factory function to create router with Discord public key from environment."""
    public_key = os.getenv("DISCORD_PUBLIC_KEY")
    if not public_key:
        raise ValueError("DISCORD_PUBLIC_KEY environment variable not set")

    return InteractionRouter(public_key)
