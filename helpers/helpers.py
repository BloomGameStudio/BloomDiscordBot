"""
shared/helpers.py is responsible for setting up helper functions for the bot.
helper functions may be functions that contain functionality that is used by multiple
modules.

The functions in this module are:
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
import discord
import requests
import subprocess
import os
from typing import Optional, Dict, Any, List, Tuple
from logger.logger import logger
from web3 import Web3
from urllib.parse import urljoin

env = os.environ.copy()


def modify_space_settings(quorum_value):
    """
    Modify Snapshot space settings using the specified quorum value.

    Parameters:
    quorum_value (int): The quorum value to set in the space settings.

    Raises:
    subprocess.CalledProcessError: If an error occurs while modifying the space settings.
    """
    command = ["node", "./snapshot/modify_space.js", str(quorum_value)]

    env["SNAPSHOT_HUB"] = cfg.SNAPSHOT_HUB
    env["SNAPSHOT_SPACE"] = cfg.SNAPSHOT_SPACE
    env["NETWORK"] = cfg.NETWORK_ID
    env["SETTINGS_NAME"] = cfg.SETTINGS_NAME
    env["SETTINGS_ABOUT"] = cfg.SETTINGS_ABOUT
    env["SETTINGS_SYMBOL"] = cfg.SETTINGS_SYMBOL
    env["SETTINGS_MEMBERS"] = ",".join(cfg.SETTINGS_MEMBERS)
    env["SETTINGS_STRATEGIES"] = cfg.SETTINGS_STRATEGIES

    try:
        subprocess.run(command, check=True, env=env)
        logger.info("Snapshot space settings modified successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error modifying snapshot space settings: {e}")
        raise


def create_snapshot_proposal(proposal_data, title):
    """
    Create a Snapshot proposal using the proposal data.

    Parameters:
    proposal_data (Dict): The proposal data to create the proposal with.
    title (str): The title of the proposal.

    Raises:
    subprocess.CalledProcessError: If an error occurs while creating the proposal
    """
    proposal_command = [
        "node",
        "./snapshot/wrapper.js",
        title,
        proposal_data["draft"]["abstract"],
        proposal_data["draft"]["background"],
        proposal_data["draft"]["additional"],
        "Adopt",
        "Reassess",
        "Abstain",
    ]

    env["SNAPSHOT_HUB"] = cfg.SNAPSHOT_HUB
    env["SNAPSHOT_SPACE"] = cfg.SNAPSHOT_SPACE
    env["NETWORK"] = cfg.NETWORK_ID
    env["PRIMARY_RPC_URL"] = cfg.PRIMARY_RPC_URL
    env["SECONDARY_RPC_URL"] = cfg.SECONDARY_RPC_URL

    try:
        subprocess.run(proposal_command, check=True, env=env)
        logger.info("Snapshot proposal created successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating snapshot proposal: {e}")
        raise


def fetch_XP_total_supply() -> int:
    """
    Fetch the total supply of tokens across all specified addresses and convert it to ether.

    Returns:
    int: The total supply of all tokens converted to ether.
    """

    primary_rpc = cfg.PRIMARY_RPC_URL
    secondary_rpc = cfg.SECONDARY_RPC_URL

    if not primary_rpc or not secondary_rpc:
        logger.error("RPC URLs not set in environment variables.")
        return None

    web3 = Web3(Web3.HTTPProvider(primary_rpc))

    if not web3.is_connected():
        logger.error("Failed to connect to PRIMARY_RPC, let's try the SECONDARY_RPC")
        web3 = Web3(Web3.HTTPProvider(secondary_rpc))
        if not web3.is_connected():
            logger.error("Failed to connect to SECONDARY_RPC, shutting down")
            exit(1)

    token_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function",
        }
    ]

    total_supply_sum = 0

    for address in cfg.SETTINGS_TOKEN_ADDRESSES:
        try:
            checksum_address = Web3.to_checksum_address(address)
            token_contract = web3.eth.contract(address=checksum_address, abi=token_abi)
            total_supply = token_contract.functions.totalSupply().call()
            if total_supply is not None:
                logger.info(
                    f"The total supply of the token at address {address} is {total_supply}."
                )
                total_supply_sum += total_supply
        except Exception as e:
            logger.error(
                f"An error occurred while fetching the total supply for address {address}: {str(e)}"
            )

    logger.info(f"The total supply of all tokens is {total_supply_sum}.")

    return total_supply_sum


def fetch_XP_quorum(percentage: int = 25) -> int:
    """
    Calculate a percentage of the total supply of tokens.

    Parameters:
    percentage (int): The percentage of the total supply to calculate (default is 25%).

    Returns:
    int: The calculated percentage of the total supply as an integer.
    """
    total_supply_sum = fetch_XP_total_supply()

    if total_supply_sum is None:
        logger.error("Failed to fetch total supply.")
        return None

    web3 = Web3()
    total_supply_in_ether = web3.from_wei(total_supply_sum, "ether")
    quorum = (total_supply_in_ether * percentage) // 100

    logger.info(f"{percentage}% of the total supply is {quorum}.")

    return quorum


def fetch_first_open_proposal_url(concluded_proposal_title):
    url = urljoin(cfg.SNAPSHOT_HUB, "graphql")
    query = """
    query {
        proposals (
            first: 1,
            where: {
                space: "%s",
                state: "open"
            },
            orderBy: "created",
            orderDirection: desc
        ) {
            id
            title
        }
    }
    """ % (
        cfg.SNAPSHOT_SPACE
    )

    response = requests.post(url, json={"query": query})

    if response.status_code == 200:
        data = response.json()
        proposals = data.get("data", {}).get("proposals", [])
        if proposals and proposals[0]["title"] == concluded_proposal_title:
            proposal_id = proposals[0]["id"]
            base_url = urljoin(cfg.SNAPSHOT_URL_PREFIX, f"{cfg.SNAPSHOT_SPACE}/")
            proposal_url = urljoin(base_url, f"proposal/{proposal_id}")
            return proposal_url
        else:
            return None
    else:
        raise Exception(
            f"Query failed with status code {response.status_code}. {response.text}"
        )


def get_channel_by_name(guild: discord.Guild, channel_name: str) -> discord.TextChannel:
    """
    Soft match a channel name from consts/constants.py to a channel in the guild. If the primary
    constant name does not exist, try to match the fallback mapping.

    Parameters:
    guild (discord.Guild): The guild to search for the channel in.
    channel_name (str): The name of the channel to search for.

    Returns:
    discord.TextChannel: The channel that matches the channel_name.

    Raises:
    ValueError: If no channel containing the channel_name exists in the guild or its fallback mapping.
    """

    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) and channel.name == channel_name:
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
        "\n Check the channel names in consts/constants.py and make sure they match the channel names in your Discord server."
    )


async def get_forum_channel_by_name(
    guild: discord.Guild, channel_name: str
) -> Optional[discord.ForumChannel]:
    """
    Retrieve a ForumChannel in a guild based on its name, with support for a fallback channel name.

    Parameters:
    - guild (discord.Guild): The guild in which to search for the ForumChannel.
    - channel_name (str): The name of the ForumChannel to search for.

    Returns:
    Optional[discord.ForumChannel]: The ForumChannel that matches the channel_name, or its fallback channel name.
    If no matching ForumChannel is found, None is returned.

    If the preferred ForumChannel name is not found, this function tries to use the fallback mapping
    to retrieve the ForumChannel with the fallback name.
    """
    for channel in guild.channels:
        if isinstance(channel, discord.ForumChannel) and channel.name == channel_name:
            return channel

    fallback_channel_name = constants.CONSTANT_FALLBACK_MAPPING.get(channel_name)
    if fallback_channel_name:
        for channel in guild.channels:
            if (
                isinstance(channel, discord.ForumChannel)
                and channel.name == fallback_channel_name
            ):
                return channel

    return None


async def get_guild_member_check_role(interaction: discord.Interaction) -> bool:
    """
    Check if the guild member who invoked the command has the 'core' role.

    Parameters:
    ctx (discord.ext.commands.Context): The context in which the command was invoked.

    Returns:
    bool: True if the member has the 'core' role, False otherwise.
    """

    member = await interaction.guild.fetch_member(interaction.user.id)
    permitted = False  # default value

    if any(role.name.lower() == "core" for role in member.roles):
        permitted = True

    if not permitted:
        await interaction.followup.send(
            "You do not have permission to use this command."
        )

    return permitted


def update_json_file(server_name: str, server_data: Dict[str, Any]) -> None:
    """
    Update emotes/contributors.json with the new contributor and emoji ID mapping.

    Parameters:
    server_name (str): The name of the server to update.
    server_data (Dict[str, Any]): The data to update the server with.
    """
    with open(cfg.CONTRIBUTORS_FILE_PATH, "r") as json_file:
        data = json.load(json_file)

    data["servers"][server_name] = server_data

    with open(cfg.CONTRIBUTORS_FILE_PATH, "w") as json_file:
        json.dump(data, json_file, indent=4)


async def send_dm_once(
    bot: discord.Client, user: discord.User, message_link: str
) -> None:
    """
    Sends a direct message to a contributor if they are mentioned in a message.
    A contributor can be mentioned via a react, or in a message itself.
    To mention a contributor you must use their emoji.
    The contributor needs to exist in emotes/contributors.json for the contributor to be mentioned.

    Parameters:
    bot (discord.Client): The bot instance.
    user (discord.User): The user to send a DM to.
    message_link (str): The link to the message that mentioned the contributor.
    """
    logger.info("Attempting to send DM")
    try:
        dm_message = f"Hello {user.display_name}! You have been mentioned in this message! {message_link}"
        await user.send(dm_message)
    except Exception as e:
        logger.error(e)


def load_posted_events() -> List[int]:
    """
    Load the event IDs that have already been posted to Discord from the JSON file.

    Returns:
    List[int]: The list of event IDs that have already been posted to Discord.
    """
    try:
        logger.info(f"Loading events from: {cfg.POSTED_EVENTS_FILE_PATH}")
        with open(cfg.POSTED_EVENTS_FILE_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def update_ongoing_votes_file(data, file_path):
    """
    Update ongoing_votes.json with the new data.

    Parameters:
    data (Dict): The data to update the ongoing_votes with.
    file_path (str): The file path to ongoing_votes.json.
    """
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


# NOTE: Should this be part of the configuration (config/config.py)?
def load_contributors_and_emoji_dicts() -> (
    Tuple[Dict[str, List[Dict[str, str]]], Dict[str, Dict[str, str]]]
):
    """
    Load the contributors and emoji dictionaries from the JSON file.

    Returns:
    Tuple[Dict[str, List[Dict[str, str]]], Dict[str, Dict[str, str]]]: The contributors and emoji dictionaries.
    """
    logger.info(
        "Loading contributors and emoji dictionaries from: "
        + cfg.CONTRIBUTORS_FILE_PATH
    )
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


def load_ongoing_votes() -> Dict[str, Any]:
    """
    Load the ongoing votes from the JSON file.

    Returns:
    Dict[str, Any]: The dictionary of ongoing votes.
    """
    try:
        logger.info(f"Loading ongoing votes from: {cfg.ONGOING_VOTES_FILE_PATH}")
        with open(cfg.ONGOING_VOTES_FILE_PATH, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    except FileNotFoundError:
        return {}
