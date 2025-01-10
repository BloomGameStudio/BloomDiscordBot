"""
utils contains utility functions that are used across multiple modules in the bot.

The module contains the following functions:
- modify_space_settings: Modify the settings of the Snapshot space.
- create_snapshot_proposal: Create a Snapshot proposal.
- fetch_XP_total_supply: Fetch the total supply of XP tokens.
- fetch_XP_quorum: Fetch the quorum value for Snapshot proposals.
- fetch_first_open_proposal_url: Fetch the URL of the first open proposal on Snapshot.
- get_channel_by_name: Soft match a channel name from consts/constants.py to a channel in the guild.
- get_forum_channel_by_name: Retrieve a ForumChannel in a guild based on its name, with support for a fallback channel name.
- get_guild_member_check_role: Check if the guild member who invoked the command has the 'core' role.
- update_json_file: Update emotes/contributors.json with the new contributor and emoji ID mapping.
- send_dm_once: Sends a direct message to a contributor if they are mentioned in a message.
- load_posted_events: Load the event IDs that have already been posted to Discord from the JSON file.
- load_contributors_and_emoji_dicts: Load the contributors and emoji dictionaries from the JSON file.
- fetch_first_open_proposal_url: Fetch the URL of the first open proposal on Snapshot.
"""

import discord
import json
import consts.constants as constants
import config.config as cfg
import requests
import subprocess
import os
from typing import Dict, Any, List, Tuple
from logger.logger import logger
from web3 import Web3
from urllib.parse import urljoin

env = os.environ.copy()


class Utils:
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
        env["NETWORK"] = cfg.NETWORK_ID
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
    def create_snapshot_proposal(proposal_data: Dict[str, Any], title: str) -> None:
        """Create a Snapshot proposal with structured sections"""
        try:
            draft = proposal_data.get("draft", {})
            sections = draft.get("sections", {})
            
            # Order sections
            section_order = ["Authors", "Definitions", "Abstract", "Background", "Implementation Protocol"]
            
            messages = []
            for section in section_order:
                if sections.get(section):
                    messages.append(f"**{section}**\n{sections[section]}")
            
            formatted_sections = {
                "messages": messages
            }

            proposal_command = [
                "node",
                "./snapshot/wrapper.js",
                title,
                json.dumps(formatted_sections),
                "Adopt",
                "Reassess",
                "Abstain"
            ]

            env = os.environ.copy()
            env.update({
                "SNAPSHOT_HUB": cfg.SNAPSHOT_HUB,
                "SNAPSHOT_SPACE": cfg.SNAPSHOT_SPACE,
                "NETWORK": cfg.NETWORK_ID,
                "PRIMARY_RPC_URL": cfg.PRIMARY_RPC_URL,
                "SECONDARY_RPC_URL": cfg.SECONDARY_RPC_URL
            })

            subprocess.run(proposal_command, check=True, env=env)
            logger.info("Snapshot proposal created successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating snapshot proposal: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating snapshot proposal: {e}")
            raise

    @staticmethod
    def fetch_XP_total_supply() -> float:
        """Fetch total XP supply with fallback and better error handling"""
        try:
            logger.info(f"Attempting to connect to PRIMARY_RPC: {cfg.PRIMARY_RPC_URL}")
            w3 = Web3(Web3.HTTPProvider(cfg.PRIMARY_RPC_URL, request_kwargs={'timeout': 10}))
            if not w3.is_connected():
                logger.error("Failed to connect to PRIMARY_RPC")
                logger.info(f"Attempting to connect to SECONDARY_RPC: {cfg.SECONDARY_RPC_URL}")
                w3 = Web3(Web3.HTTPProvider(cfg.SECONDARY_RPC_URL, request_kwargs={'timeout': 10}))
                if not w3.is_connected():
                    logger.error("Failed to connect to SECONDARY_RPC")
                    return 0

            contract = w3.eth.contract(
                address=Web3.to_checksum_address(cfg.XP_CONTRACT_ADDRESS),
                abi=cfg.XP_CONTRACT_ABI
            )
            total_supply = contract.functions.totalSupply().call()
            return float(total_supply) / (10 ** 18)

        except Exception as e:
            logger.error(f"Error fetching XP total supply: {e}")
            return 0

    @staticmethod
    def fetch_XP_quorum(percentage: int = 25) -> int:
        """
        Fetch the quorum value for Snapshot proposals.

        Parameters:
        percentage (int): The percentage of the total supply to set as the quorum value (default 25).

        Returns:
        int: The quorum value for Snapshot proposals.
        """
        total_supply_sum = Utils.fetch_XP_total_supply()
        if total_supply_sum is None:
            logger.error("Failed to fetch total supply.")
            return None

        web3 = Web3()
        total_supply_in_ether = web3.from_wei(total_supply_sum, "ether")
        quorum = (total_supply_in_ether * percentage) // 100
        logger.info(f"{percentage}% of the total supply is {quorum}.")
        return quorum

    @staticmethod
    def fetch_first_open_proposal_url(concluded_proposal_title):
        """
        Fetch the URL of the first open proposal on Snapshot.

        Parameters:
        concluded_proposal_title (str): The title of the concluded proposal.

        Returns:
        str: The URL of the first open proposal on Snapshot.

        Raises:
        Exception: If the query to fetch the URL fails.
        """
        url = urljoin(cfg.SNAPSHOT_HUB, "graphql")
        query = f"""
        query {{
            proposals (
                first: 1,
                where: {{
                    space: "{cfg.SNAPSHOT_SPACE}",
                    state: "open"
                }},
                orderBy: "created",
                orderDirection: desc
            ) {{
                id
                title
            }}
        }}
        """
        response = requests.post(url, json={"query": query})
        if response.status_code == 200:
            data = response.json()
            proposals = data.get("data", {}).get("proposals", [])
            if proposals and proposals[0]["title"] == concluded_proposal_title:
                proposal_id = proposals[0]["id"]
                base_url = f"{cfg.SNAPSHOT_URL_PREFIX}#/{cfg.SNAPSHOT_SPACE}/"
                proposal_url = f"{base_url}proposal/{proposal_id}"
                return proposal_url
            else:
                return None
        else:
            raise Exception(
                f"Query failed with status code {response.status_code}. {response.text}"
            )

    @staticmethod
    def get_channel_by_name(
        guild: discord.Guild, channel_name: str
    ) -> discord.TextChannel:
        """
        Soft match a channel name from consts/constants.py to a channel in the guild.

        Parameters:
        guild (Guild): The guild to search for the channel in.
        channel_name (str): The name of the channel to search for.

        Returns:
        TextChannel: The channel with the matching name.

        Raises:
        ValueError: If no channel containing the name exists in the guild.
        """
        for channel in guild.channels:
            if (
                isinstance(channel, discord.TextChannel)
                and channel.name == channel_name
            ):
                return channel

        fallback_channel_name = constants.CONSTANT_FALLBACK_MAPPING.get(channel_name)
        if fallback_channel_name:
            for channel in guild.channels:
                if (
                    isinstance(channel, discord.TextChannel)
                    and channel.name == fallback_channel_name
                ):
                    return channel
        raise ValueError(
            f"No channel containing the name {channel_name} or {fallback_channel_name} exists in the guild {guild}."
        )

    @staticmethod
    async def get_guild_member_check_role(interaction: discord.Interaction) -> bool:
        """
        Check if the guild member who invoked the command has the 'core' role.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.

        Returns:
        bool: True if the member has the 'core' role, False otherwise.
        """
        member = await interaction.guild.fetch_member(interaction.user.id)
        if any(role.name.lower() == "core" for role in member.roles):
            return True
        await interaction.followup.send(
            "You do not have permission to use this command."
        )
        return False

    @staticmethod
    def update_json_file(server_name: str, server_data: Dict[str, Any]) -> None:
        """
        Update emotes/contributors.json with the new contributor and emoji ID mapping.

        Parameters:
        server_name (str): The name of the server.
        server_data (Dict[str, Any]): The data to update the JSON file with.
        """
        with open(cfg.CONTRIBUTORS_FILE_PATH, "r") as json_file:
            data = json.load(json_file)
        data["servers"][server_name] = server_data
        with open(cfg.CONTRIBUTORS_FILE_PATH, "w") as json_file:
            json.dump(data, json_file, indent=4)

    @staticmethod
    async def send_dm_once(
        bot: discord.Client, user: discord.User, message_link: str
    ) -> None:
        """
        Sends a direct message to a contributor if they are mentioned in a message.

        Parameters:
        bot (discord.Client): The bot instance.
        user (discord.User): The user to send the message to.
        message_link (str): The link to the message that mentions the user.
        """
        try:
            dm_message = f"Hello {user.display_name}! You have been mentioned in this message! {message_link}"
            await user.send(dm_message)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def load_posted_events() -> List[int]:
        """
        Load the event IDs that have already been posted to Discord from the JSON file.

        Returns:
        List[int]: The list of event IDs.
        """
        logger.info("Loading posted events")
        try:
            with open(cfg.POSTED_EVENTS_FILE_PATH, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    @staticmethod
    def load_contributors_and_emoji_dicts() -> (
        Tuple[Dict[str, List[Dict[str, str]]], Dict[str, Dict[str, str]]]
    ):
        """
        Load the contributors and emoji dictionaries from the JSON file.

        Returns:
        Tuple[Dict[str, List[Dict[str, str]], Dict[str, Dict[str, str]]]: The dictionaries of contributors and emojis.
        """
        logger.info("Loading contributors and emoji dictionaries")
        with open(cfg.CONTRIBUTORS_FILE_PATH, "r") as json_file:
            data = json.load(json_file)
        contributors = {
            "Bloom Studio": data["servers"]["Bloom Studio"]["contributors"],
            "Bloom Collective": data["servers"]["Bloom Collective"]["contributors"],
        }
        emoji_dicts = {
            "Bloom Studio": data["servers"]["Bloom Studio"]["emoji_dictionary"],
            "Bloom Collective": data["servers"]["Bloom Collective"]["emoji_dictionary"],
        }
        return contributors, emoji_dicts

    @staticmethod
    def load_ongoing_votes() -> Dict[str, Any]:
        """
        Load the ongoing votes from the JSON file.

        Returns:
        Dict[str, Any]: The dictionary of ongoing votes.
        """
        logger.info("Loading ongoing votes")
        try:
            with open(cfg.ONGOING_VOTES_FILE_PATH, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def update_ongoing_votes_file(data, file_path):
        """
        Update the ongoing votes in the JSON file.

        Parameters:
        data (Dict[str, Any]): The dictionary of ongoing votes.
        file_path (str): The path to the JSON file.

        Returns:
        None
        """
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    @staticmethod
    def load_notified_events() -> Dict[str, Any]:
        """
        Load the notified events from the JSON file.

        Returns:
        Dict[str, Any]: The dictionary of notified events.
        """
        logger.info("Loading notified events")
        if os.path.exists(cfg.NOTIFIED_EVENTS_FILE_PATH):
            if os.path.getsize(cfg.NOTIFIED_EVENTS_FILE_PATH) == 0:
                return {}

            try:
                with open(cfg.NOTIFIED_EVENTS_FILE_PATH, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON format in {cfg.NOTIFIED_EVENTS_FILE_PATH}")
                return {}
        return {}

    @staticmethod
    def save_notified_events(notified_events: Dict[str, Any]) -> None:
        """
        Save the notified events to the JSON file.

        Parameters:
        notified_events (Dict[str, Any]): The dictionary of notified events.
        """
        logger.info(f"Saving notified events to {cfg.NOTIFIED_EVENTS_FILE_PATH}")
        with open(cfg.NOTIFIED_EVENTS_FILE_PATH, "w") as file:
            json.dump(notified_events, file, indent=4)
