"""
utils contains utility functions that are used across multiple modules in the bot.

The module contains the following functions:
- modify_space_settings: Modify the settings of the Snapshot space.
- create_snapshot_proposal: Create a Snapshot proposal.
- fetch_XP_total_supply: Fetch the total supply of XP tokens.
- fetch_XP_quorum: Fetch the quorum value for Snapshot proposals.
- get_proposal_url: Fetch the URL of the Snapshot proposal or space.
- get_channel_by_name: Soft match a channel name from consts/constants.py to a channel in the guild.
- get_forum_channel_by_name: Retrieve a ForumChannel in a guild based on its name, with support for a fallback channel name.
- get_guild_member_check_role: Check if the guild member who invoked the command has the 'core' role.
- update_json_file: Update emotes/contributors.json with the new contributor and emoji ID mapping.
- send_dm_once: Sends a direct message to a contributor if they are mentioned in a message.
- load_posted_events: Load the event IDs that have already been posted to Discord from the JSON file.
- load_contributors_and_emoji_dicts: Load the contributors and emoji dictionaries from the JSON file.
"""

import discord
import json
import subprocess
import os
from typing import Dict, Any, Optional
from web3 import Web3

import config.config as cfg
from logger.logger import logger
from discord.ext import commands

env = os.environ.copy()


class DiscordUtils:
    @staticmethod
    async def get_channel_by_name(guild, channel_name: str):
        """
        Get a channel by name from a guild.

        Parameters:
        guild (discord.Guild): The guild to search in
        channel_name (str): The name of the channel to find

        Returns:
        discord.TextChannel: The found channel

        Raises:
        ValueError: If channel is not found
        """
        channel = discord.utils.get(guild.channels, name=channel_name)
        if not channel:
            raise ValueError(
                f"Channel '{channel_name}' not found in guild {guild.name}"
            )
        return channel

    @staticmethod
    async def get_guild_member_check_role(interaction: discord.Interaction) -> bool:
        """Check if the guild member who invoked the command has the 'core' role"""
        member = await interaction.guild.fetch_member(interaction.user.id)
        if any(role.name.lower() == "core" for role in member.roles):
            return True
        await interaction.followup.send(
            "You do not have permission to use this command."
        )
        return False

    @staticmethod
    async def send_dm_once(
        bot: discord.Client, user: discord.User, message_link: str
    ) -> None:
        """Sends a direct message to a contributor if they are mentioned in a message"""
        try:
            dm_message = f"Hello {user.display_name}! You have been mentioned in this message! {message_link}"
            await user.send(dm_message)
        except Exception as e:
            logger.error(e)


class SnapshotUtils:
    @staticmethod
    def fetch_XP_quorum(percentage: int = 25) -> int:
        """
        Fetch the quorum value for Snapshot proposals.

        Parameters:
        percentage (int): The percentage of the total supply to set as the quorum value (default 25).

        Returns:
        int: The quorum value for Snapshot proposals.
        """
        total_supply = Utils.fetch_XP_total_supply()
        if total_supply is None:
            logger.error("Failed to fetch total supply.")
            return None

        quorum = int((total_supply * percentage) // 100)
        logger.info(f"{percentage}% of the total supply is {quorum}.")
        return quorum

    @staticmethod
    def modify_space_settings(quorum_value):
        """
        Modify the settings of the Snapshot space.

        Parameters:
        quorum_value (int): The new quorum value to set for the Snapshot space

        Raises:
        subprocess.CalledProcessError: If the subprocess call to modify the space settings fails.
        """
        command = ["node", "./snapshot/modify_space.js", str(quorum_value)]
        env["SNAPSHOT_HUB"] = cfg.SNAPSHOT_HUB
        env["SNAPSHOT_SPACE"] = cfg.SNAPSHOT_SPACE
        env["NETWORK_ID"] = cfg.NETWORK_ID
        env["SETTINGS_NAME"] = cfg.SETTINGS_NAME
        env["SETTINGS_ABOUT"] = cfg.SETTINGS_ABOUT
        env["SETTINGS_SYMBOL"] = cfg.SETTINGS_SYMBOL
        env["SETTINGS_MEMBERS"] = ",".join(cfg.SETTINGS_MEMBERS)
        env["SETTINGS_ADMINS"] = ",".join(cfg.SETTINGS_ADMINS)
        env["SETTINGS_STRATEGIES"] = cfg.SETTINGS_STRATEGIES

        try:
            subprocess.run(command, check=True, env=env)
            logger.info("Snapshot space settings modified successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error modifying snapshot space settings: {e}")
            raise

    @staticmethod
    def create_snapshot_proposal(
        proposal_data: Dict[str, Any], title: str
    ) -> Optional[object]:
        """Create a Snapshot proposal with structured sections"""
        try:
            draft = proposal_data.get("draft", {})
            sections = draft.get("sections", {})
            content = sections.get("content", "")
            formatted_sections = {"messages": [content]}
            resultPrefix = "RESULT: "

            proposal_command = [
                "node",
                "./snapshot/wrapper.js",
                title,
                resultPrefix,
                json.dumps(formatted_sections),
                "Adopt",
                "Reassess",
                "Abstain",
            ]

            env = os.environ.copy()
            env.update(
                {
                    "SNAPSHOT_HUB": cfg.SNAPSHOT_HUB,
                    "SNAPSHOT_SPACE": cfg.SNAPSHOT_SPACE,
                    "NETWORK_ID": cfg.NETWORK_ID,
                    "PRIMARY_RPC_URL": cfg.PRIMARY_RPC_URL,
                    "SECONDARY_RPC_URL": cfg.SECONDARY_RPC_URL,
                }
            )

            receipt = None
            result = subprocess.run(
                proposal_command, check=True, env=env, capture_output=True, text=True
            )

            for line in result.stdout.splitlines():
                if line.startswith(resultPrefix):  # Identify result line
                    try:
                        receipt = json.loads(line[len(resultPrefix) :])
                        print("Parsed receipt:", receipt)
                    except json.JSONDecodeError:
                        print("Failed to parse JSON:", line)
                        logger.info("Snapshot proposal created successfully.")

            if receipt == None:
                logger.info("No receipt was returned")

            return receipt
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating snapshot proposal: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating snapshot proposal: {e}")
            raise

    @staticmethod
    def get_proposal_url(receipt: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Get the URL for the Snapshot proposal or space.

        Parameters:
        receipt (Optional[Dict[str, Any]]): Receipt returned from the proposal creation subprocess

        Returns:
        Optional[str]: The URL of the Snapshot proposal or space
        """

        id = None
        if receipt:
            id = receipt.get("id", None)

        try:
            url = f"{cfg.SNAPSHOT_URL_PREFIX}#/s:{cfg.SNAPSHOT_SPACE}/" + (
                f"proposal/{id}" if id is not None else ""
            )
            logger.info(f"Generated Snapshot space URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Error generating Snapshot space URL: {e}")
            return None

    @staticmethod
    async def fetch_XP_quorum(
        bot: Optional[commands.Bot] = None,
        guild_id: Optional[int] = None,
        percentage: int = 25,
    ) -> int:
        """
        Fetch the quorum value for Snapshot proposals.

        Parameters:
        bot (Optional[commands.Bot]): The bot instance for Discord-specific quorum
        guild_id (Optional[int]): The ID of the guild for Discord-specific quorum
        percentage (int): The percentage of total supply for Snapshot quorum (default 25)

        Returns:
        int: The quorum value
        """
        if bot and guild_id:
            try:
                return cfg.YES_COUNT_THRESHOLD
            except Exception as e:
                logger.error(f"Error fetching Discord quorum: {e}")
                return 5
        else:
            total_supply = Utils.fetch_XP_total_supply()
            if total_supply is None:
                logger.error("Failed to fetch total supply.")
                return None

            quorum = int((total_supply * percentage) // 100)
            logger.info(f"{percentage}% of the total supply is {quorum}.")
            return quorum


class Utils:
    @staticmethod
    def fetch_XP_total_supply() -> float:
        """Fetch total XP supply with fallback and better error handling"""
        try:
            logger.info(f"Attempting to connect to PRIMARY_RPC: {cfg.PRIMARY_RPC_URL}")
            w3 = Web3(
                Web3.HTTPProvider(cfg.PRIMARY_RPC_URL, request_kwargs={"timeout": 10})
            )
            if not w3.is_connected():
                logger.error("Failed to connect to PRIMARY_RPC")
                logger.info(
                    f"Attempting to connect to SECONDARY_RPC: {cfg.SECONDARY_RPC_URL}"
                )
                w3 = Web3(
                    Web3.HTTPProvider(
                        cfg.SECONDARY_RPC_URL, request_kwargs={"timeout": 10}
                    )
                )
                if not w3.is_connected():
                    logger.error("Failed to connect to SECONDARY_RPC")
                    return 0

            total_supply = 0
            # Basic ERC20 totalSupply ABI
            abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "totalSupply",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "payable": False,
                    "stateMutability": "view",
                    "type": "function",
                }
            ]

            for address in cfg.SETTINGS_TOKEN_ADDRESSES:
                try:
                    contract = w3.eth.contract(
                        address=Web3.to_checksum_address(address.strip()), abi=abi
                    )
                    supply = contract.functions.totalSupply().call()
                    total_supply += supply
                    logger.info(
                        f"Successfully fetched supply for token {address}: {supply}"
                    )
                except Exception as e:
                    logger.error(f"Error fetching supply for token {address}: {e}")
                    continue

            return float(total_supply) / (10**18)

        except Exception as e:
            logger.error(f"Error fetching XP total supply: {e}")
            return 0

    @staticmethod
    def get_channel_by_name(guild, channel_name: str):
        """
        Get a channel by name from a guild.

        Parameters:
        guild (discord.Guild): The guild to search in
        channel_name (str): The name of the channel to find

        Returns:
        discord.TextChannel: The found channel

        Raises:
        ValueError: If channel is not found
        """
        channel = discord.utils.get(guild.channels, name=channel_name)
        if not channel:
            raise ValueError(
                f"Channel '{channel_name}' not found in guild {guild.name}"
            )
        return channel
