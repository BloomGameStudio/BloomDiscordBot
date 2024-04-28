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
from typing import Optional, Dict, Any, List, Tuple
from logger.logger import logger


def fetch_first_open_proposal_url(concluded_proposal_title):
    url = "https://hub.snapshot.org/graphql"
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
        constants.SNAPSHOT_SPACE
    )

    response = requests.post(url, json={"query": query})

    if response.status_code == 200:
        data = response.json()
        proposals = data.get("data", {}).get("proposals", [])
        if proposals and proposals[0]["title"] == concluded_proposal_title:
            proposal_id = proposals[0]["id"]
            return f"https://snapshot.org/#/{constants.SNAPSHOT_SPACE}/proposal/{proposal_id}"
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

    # try to find the preferred channel name directly
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) and channel.name == channel_name:
            return channel

    # If the preferred channel is not found, try to use the fallback mapping
    fallback_channel_name = constants.CONSTANT_FALLBACK_MAPPING.get(channel_name)
    if (
        fallback_channel_name
    ):  # If a fallback name is defined for the given channel_name
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
    # First, try to find the preferred forum channel name directly
    for channel in guild.channels:
        if isinstance(channel, discord.ForumChannel) and channel.name == channel_name:
            return channel

    # If the preferred forum channel is not found, try to use the fallback mapping
    fallback_channel_name = constants.CONSTANT_FALLBACK_MAPPING.get(channel_name)
    if (
        fallback_channel_name
    ):  # If a fallback name is defined for the given channel_name
        for channel in guild.channels:
            if (
                isinstance(channel, discord.ForumChannel)
                and channel.name == fallback_channel_name
            ):
                return channel

    return None  # Return None if neither the channel_name nor the fallback mapping is found


async def get_guild_member_check_role(interaction: discord.Interaction) -> bool:
    """
    Check if the guild member who invoked the command has the 'core' role.

    Parameters:
    ctx (discord.ext.commands.Context): The context in which the command was invoked.

    Returns:
    bool: True if the member has the 'core' role, False otherwise.
    """

    # Retrieve the guild member who invoked the command
    member = await interaction.guild.fetch_member(interaction.user.id)
    permitted = False  # default value

    # Check if they have the 'core' role.
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
    # Read the existing data
    with open(cfg.CONTRIBUTORS_FILE_PATH, "r") as json_file:
        data = json.load(json_file)

    # Update the specific server's data
    data["servers"][server_name] = server_data

    # Write the updated data back to the file
    with open(cfg.CONTRIBUTORS_FILE_PATH, "w") as json_file:
        json.dump(data, json_file, indent=4)


async def send_dm_once(
    bot: discord.Client, contributor: Dict[str, str], message_link: str
) -> None:
    """
    Sends a direct message to a contributor if they are mentioned in a message.
    A contributor can be mentioned via a react, or in a message itself.
    To mention a contributor you must use their emoji.
    The contributor needs to exist in emotes/contributors.json for the contributor to be mentioned.

    Parameters:
    bot (discord.Client): The bot instance.
    contributor (Dict[str, str]): The contributor to send a DM to.
    message_link (str): The link to the message that mentioned the contributor.
    """

    user = await bot.fetch_user(int(contributor["uid"]))
    if user:
        dm_message = f"Hello {user.name}! You have been mentioned in this message! {message_link}"
        await user.send(dm_message)


# Load the stored events from the JSON file
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
    # Write the updated data to the file
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
