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
from typing import Dict, Any, List, Tuple, Optional
from logger.logger import logger
from web3 import Web3
from urllib.parse import urljoin
from database.models import SessionLocal, Contributor, Event, OngoingVote, ConcludedVote, Config
import time

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
    def create_snapshot_proposal(proposal_data: Dict[str, Any], title: str) -> None:
        """Create a Snapshot proposal with structured sections"""
        try:
            draft = proposal_data.get("draft", {})
            sections = draft.get("sections", {})

            # Get the raw content and split into messages
            content = sections.get("content", "")

            # Format the content for Snapshot
            formatted_sections = {
                "messages": [content]  # Pass the entire content as a single message
            }

            proposal_command = [
                "node",
                "./snapshot/wrapper.js",
                title,
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
                    "NETWORK": cfg.NETWORK_ID,
                    "PRIMARY_RPC_URL": cfg.PRIMARY_RPC_URL,
                    "SECONDARY_RPC_URL": cfg.SECONDARY_RPC_URL,
                }
            )

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

    @staticmethod
    def update_contributor_in_db(
        guild_id: int, uid: str, note: str, emoji_id: str
    ) -> None:
        """Update or create a contributor in the database"""
        with SessionLocal() as session:
            contributor = (
                session.query(Contributor)
                .filter_by(server_name=str(guild_id), uid=uid)
                .first()
            )

            if contributor:
                contributor.note = note
                contributor.emoji_id = emoji_id
            else:
                contributor = Contributor(
                    uid=uid, note=note, server_name=str(guild_id), emoji_id=emoji_id
                )
                session.add(contributor)

            session.commit()

    @staticmethod
    def get_contributors_from_db(guild_id: int) -> List[Contributor]:
        """Get list of contributors for a specific server"""
        with SessionLocal() as session:
            contributors = session.query(Contributor).filter_by(server_name=str(guild_id)).all()
            return contributors

    @staticmethod
    def save_event(
        event_id: int,
        guild_id: int,
        posted_at: Optional[float] = None,
        notified_at: Optional[float] = None,
    ) -> None:
        """Save or update an event in the database"""
        with SessionLocal() as session:
            event = session.query(Event).filter_by(event_id=event_id).first()
            if event:
                if posted_at is not None:
                    event.posted_at = posted_at
                if notified_at is not None:
                    event.notified_at = notified_at
            else:
                event = Event(
                    event_id=event_id,
                    guild_id=guild_id,
                    posted_at=posted_at,
                    notified_at=notified_at,
                )
                session.add(event)
            session.commit()

    @staticmethod
    def get_posted_events() -> List[int]:
        """Get list of posted event IDs from database"""
        with SessionLocal() as session:
            events = session.query(Event).filter(Event.posted_at.isnot(None)).all()
            return [event.event_id for event in events]

    @staticmethod
    def get_notified_events() -> Dict[int, float]:
        """Get dictionary of notified events with their notification timestamps"""
        with SessionLocal() as session:
            events = session.query(Event).filter(Event.notified_at.isnot(None)).all()
            return {event.event_id: event.notified_at for event in events}

    @staticmethod
    def save_ongoing_vote(proposal_id: str, vote_data: dict):
        """Save an ongoing vote to the database"""
        with SessionLocal() as session:
            vote = (
                session.query(OngoingVote)
                .filter(OngoingVote.proposal_id == proposal_id)
                .first()
            )
            if not vote:
                vote = OngoingVote(proposal_id=proposal_id)

            vote.draft = vote_data.get("draft", {})
            vote.end_time = vote_data.get("end_time", 0)
            vote.title = vote_data.get("title", "")
            vote.channel_id = vote_data.get("channel_id", "")
            vote.thread_id = vote_data.get("thread_id", "")
            vote.message_id = vote_data.get("message_id", "")

            session.add(vote)
            session.commit()

    @staticmethod
    def get_ongoing_votes():
        """Get all ongoing votes from the database"""
        with SessionLocal() as session:
            votes = session.query(OngoingVote).all()
            return {
                vote.proposal_id: {
                    "draft": vote.draft,
                    "end_time": vote.end_time,
                    "title": vote.title,
                    "channel_id": vote.channel_id,
                    "thread_id": vote.thread_id,
                    "message_id": vote.message_id,
                }
                for vote in votes
            }

    @staticmethod
    def remove_ongoing_vote(proposal_id: str) -> None:
        """Remove an ongoing vote from the database"""
        with SessionLocal() as session:
            session.query(OngoingVote).filter_by(proposal_id=proposal_id).delete()
            session.commit()

    @staticmethod
    def save_concluded_vote(
        proposal_data: dict, passed: bool, snapshot_url: Optional[str] = None
    ) -> None:
        """Save a concluded vote to the database"""
        with SessionLocal() as session:
            vote = ConcludedVote(
                proposal_id=proposal_data["proposal_id"],
                draft=proposal_data["draft"],
                title=proposal_data["title"],
                channel_id=proposal_data["channel_id"],
                thread_id=proposal_data["thread_id"],
                message_id=proposal_data["message_id"],
                yes_count=proposal_data.get("yes_count", 0),
                no_count=proposal_data.get("no_count", 0),
                abstain_count=proposal_data.get("abstain_count", 0),
                passed=passed,
                concluded_at=time.time(),
                snapshot_url=snapshot_url,
            )
            session.add(vote)
            session.commit()

    @staticmethod
    def get_concluded_votes(passed_only: bool = False) -> Dict[str, Any]:
        """Get all concluded votes from the database

        Args:
            passed_only (bool): If True, only return proposals that passed

        Returns:
            Dict[str, Any]: Dictionary of concluded votes with their details
        """
        with SessionLocal() as session:
            query = session.query(ConcludedVote)
            if passed_only:
                query = query.filter(ConcludedVote.passed == True)

            votes = query.order_by(ConcludedVote.concluded_at.desc()).all()
            return {
                vote.proposal_id: {
                    "draft": vote.draft,
                    "title": vote.title,
                    "yes_count": vote.yes_count,
                    "no_count": vote.no_count,
                    "abstain_count": vote.abstain_count,
                    "passed": vote.passed,
                    "concluded_at": vote.concluded_at,
                    "snapshot_url": vote.snapshot_url,
                }
                for vote in votes
            }

    @staticmethod
    def remove_contributor_from_db(guild_id: int, uid: str) -> None:
        """Remove a contributor from the database"""
        try:
            with SessionLocal() as session:
                contributor = session.query(Contributor).filter_by(
                    server_name=str(guild_id),
                    uid=uid
                ).first()
                
                if not contributor:
                    logger.warning(f"No contributor found with uid={uid} in server={guild_id}")
                    return

                session.delete(contributor)
                session.commit()
                logger.info(f"Successfully removed contributor with uid={uid} from server={guild_id}")
        except Exception as e:
            logger.error(f"Error removing contributor: {e}")
            raise
