"""
tasks contains the TaskManager class, which contains the check_events and check_concluded_proposals_task functions.
"""

import time
import discord
from discord.ext import tasks, commands
import random

from logger.logger import logger
from events.event_operations import EventOperations
from utils.utils import DiscordUtils
from consts.constants import (
    GENERAL_CHANNEL,
    YES_VOTE,
    NO_VOTE,
    ABSTAIN_VOTE,
    PROPOSAL_CONCLUSION_EMOJIS,
)
import config.config as cfg
from database.service import DatabaseService
from utils.utils import SnapshotUtils


class TaskManager:
    check_concluded_proposals_task = None
    check_events_task = None

    @classmethod
    async def start_tasks(cls, bot: commands.Bot):
        """Start all scheduled tasks"""
        try:
            if not hasattr(cls, "_tasks_started"):
                cls.check_concluded_proposals_task = tasks.loop(minutes=5)(
                    cls.check_concluded_proposals
                )
                cls.check_events_task = tasks.loop(minutes=50)(cls.check_events)

                @cls.check_concluded_proposals_task.before_loop
                async def before_check_concluded_proposals():
                    await bot.wait_until_ready()

                @cls.check_events_task.before_loop
                async def before_check_events():
                    await bot.wait_until_ready()

                cls.check_concluded_proposals_task.start(bot)
                cls.check_events_task.start(bot)

                cls._tasks_started = True
                logger.info("Tasks started successfully")
        except Exception as e:
            logger.error(f"Error starting tasks: {e}")

    @classmethod
    async def check_concluded_proposals(cls, bot: commands.Bot):
        """Check for concluded proposals every 5 minutes"""
        logger.info("Checking for concluded proposals...")
        try:
            db_service = DatabaseService()
            ongoing_votes = db_service.get_ongoing_votes()

            for proposal_id, proposal_data in ongoing_votes.items():
                if time.time() < proposal_data["end_time"]:
                    continue

                channel = bot.get_channel(int(proposal_data["channel_id"]))
                if not channel:
                    logger.error(
                        f"Unable to find the channel with id: {proposal_data['channel_id']}"
                    )
                    continue

                thread = channel.get_thread(int(proposal_data["thread_id"]))
                if not thread:
                    logger.error(
                        f"Unable to find the thread with id: {proposal_data['thread_id']} in the channel: {channel.name}"
                    )
                    continue

                message = await thread.fetch_message(int(proposal_data["message_id"]))
                if not message:
                    logger.error(
                        f"Unable to find the message with id: {proposal_data['message_id']} in the thread: {thread.id}"
                    )
                    continue

                # Initialize vote counts
                proposal_data.update(
                    {"yes_count": 0, "no_count": 0, "abstain_count": 0}
                )

                counts = {
                    YES_VOTE: "yes_count",
                    NO_VOTE: "no_count",
                    ABSTAIN_VOTE: "abstain_count",
                }

                for reaction in message.reactions:
                    emoji = str(reaction.emoji)
                    if emoji in counts:
                        proposal_data[counts[emoji]] = (
                            reaction.count - 1
                        )  # Subtract bot's reaction

                logger.info(
                    f"Vote counts for {proposal_data['title']}: Yes={proposal_data['yes_count']}, No={proposal_data['no_count']}, Abstain={proposal_data['abstain_count']}"
                )

                # Save updated vote counts
                db_service.save_ongoing_vote(proposal_data)

                passed = (
                    proposal_data["yes_count"] > proposal_data["no_count"]
                    and proposal_data["yes_count"] >= cfg.YES_COUNT_THRESHOLD
                )
                result_message = (
                    f"Vote for **{proposal_data['title']}** has concluded:\n\n"
                )

                if passed:
                    draft_title = proposal_data["draft"]["title"]
                    proposal_type = proposal_data["draft"]["type"]

                    config = db_service.get_config()
                    receipt = None

                    if proposal_type == "budget":
                        budget_id = config.get("next_budget_id", "")

                        if not budget_id:
                            logger.error("Budget ID is not set")
                            continue

                        title = f"Bloom Budget Proposal #{budget_id}: {draft_title}"
                    elif proposal_type == "governance":
                        governance_id = config.get("next_governance_id", "")

                        if not governance_id:
                            logger.error("Governance ID is not set")
                            continue

                        title = (
                            f"Bloom General Proposal #{governance_id}: {draft_title}"
                        )
                    else:
                        logger.error(f"Unknown proposal type: {proposal_type}")
                        continue

                    try:
                        quorum_value = await SnapshotUtils.fetch_XP_quorum()
                        SnapshotUtils.modify_space_settings(str(quorum_value))
                        logger.info(f"Quorum value set to {quorum_value}")

                        receipt = SnapshotUtils.create_snapshot_proposal(
                            proposal_data, title
                        )
                    except Exception as e:
                        logger.error(f"Error creating snapshot proposal: {e}")
                        continue

                    proposal_url = SnapshotUtils.get_proposal_url(receipt)
                    if proposal_url:
                        result_message += f"The vote passes! {random.choice(PROPOSAL_CONCLUSION_EMOJIS)}\n\nSnapshot proposal has been created: **{proposal_url}**"
                        if proposal_type == "budget":
                            db_service.set_config(
                                "next_budget_id", str(int(budget_id) + 1)
                            )
                        elif proposal_type == "governance":
                            db_service.set_config(
                                "next_governance_id", str(int(governance_id) + 1)
                            )
                    else:
                        result_message += f"The vote passes! {random.choice(PROPOSAL_CONCLUSION_EMOJIS)}"
                else:
                    result_message += "The vote fails. :disappointed:"

                result_message += f"\nAdopt: {proposal_data['yes_count']}\nReassess: {proposal_data['no_count']}\nAbstain: {proposal_data['abstain_count']}"

                logger.info(
                    f"Yes vote count: {proposal_data['yes_count']} No vote count: {proposal_data['no_count']} Abstain vote count: {proposal_data['abstain_count']}"
                )

                try:
                    await thread.send(result_message)
                except discord.HTTPException as e:
                    logger.error(
                        f"An error occurred while posting the result message: {e}"
                    )

                guild = channel.guild
                logger.info(
                    f"Looking for general channel '{GENERAL_CHANNEL}' in guild: {guild.name}"
                )
                general_channel = await DiscordUtils.get_channel_by_name(
                    guild, GENERAL_CHANNEL
                )

                if general_channel:
                    try:
                        await general_channel.send(result_message)
                    except discord.HTTPException as e:
                        logger.error(
                            f"An error occurred while posting the result message to general channel: {e}"
                        )
                else:
                    logger.error(
                        f"Unable to find the general channel '{GENERAL_CHANNEL}' in guild: {guild.name}"
                    )

                try:
                    db_service.save_concluded_vote(
                        proposal_data=proposal_data,
                        yes_count=proposal_data.get("yes_count", 0),
                        no_count=proposal_data.get("no_count", 0),
                        abstain_count=proposal_data.get("abstain_count", 0),
                        passed=passed,
                        snapshot_url=proposal_url if passed else None,
                    )

                    db_service.remove_ongoing_vote(proposal_id)
                    logger.info(f"Successfully concluded proposal {proposal_id}")
                except Exception as e:
                    logger.error(f"Error saving/removing concluded vote: {e}")
                    continue

        except Exception as e:
            logger.error(f"An error occurred while checking ongoing proposals: {e}")

    @classmethod
    async def check_events(cls, bot: commands.Bot) -> None:
        """Check for upcoming events"""
        logger.info("Checking for upcoming events...")
        try:
            db_service = DatabaseService()
            if not hasattr(bot, "posted_events"):
                bot.posted_events = []
                posted_events = db_service.get_posted_events()
                if posted_events:
                    bot.posted_events.extend(posted_events)
                logger.info(f"Initialized posted_events: {bot.posted_events}")

            event_operations = EventOperations(bot)
            current_time = time.time()
            one_hour_ago = current_time - 3600
            logger.info(f"Checking for upcoming events")

            for guild in bot.guilds:
                try:
                    channel = await DiscordUtils.get_channel_by_name(
                        guild, GENERAL_CHANNEL
                    )
                    if not channel:
                        logger.error(f"Channel not found in guild {guild.name}")
                        continue

                    upcoming_events = await event_operations.fetch_upcoming_events(
                        guild
                    )

                    if not upcoming_events:
                        logger.info(
                            f"No upcoming events in the next 24 hours for guild {guild}."
                        )
                        continue

                    notified_events = db_service.get_notified_events()
                    new_events = [
                        event
                        for event in upcoming_events
                        if event.id not in bot.posted_events
                    ]

                    if new_events:
                        for event in new_events:
                            last_notified = notified_events.get(str(event.id), 0)

                            if last_notified > one_hour_ago:
                                logger.info(
                                    f"Skipping event {event.id} as it was recently notified"
                                )
                                continue

                            users = event_operations.get_guild_scheduled_event_users(
                                guild.id, event.id
                            )

                            guild_id = event.guild.id
                            user_mentions = [f"<@{user['user_id']}>" for user in users]
                            user_list_string = ", ".join(user_mentions)

                            formatted_event = event_operations.format_event(
                                event, guild_id
                            )

                            db_service.save_event(
                                event_id=event.id,
                                guild_id=guild_id,
                                posted_at=current_time,
                                notified_at=current_time,
                            )
                            bot.posted_events.append(event.id)

                            message = f"🌺 **__Upcoming Event__** 🌺\n{formatted_event}"
                            if user_list_string:
                                message += f"\n\nInterested users: {user_list_string}"
                            await channel.send(message)
                    else:
                        logger.info(
                            f"No new upcoming events in the next 24 hours for guild {guild}."
                        )

                except Exception as e:
                    logger.error(f"Error in check_events loop: {e}")
                    continue

        except Exception as e:
            logger.error(f"An error occurred while checking events: {e}")

    async def check_vote_results(
        self, proposal_data: dict, message: discord.Message
    ) -> bool:
        """Check if a vote has passed based on reactions"""
        reactions = message.reactions
        yes_count = 0
        no_count = 0
        abstain_count = 0

        for reaction in reactions:
            if str(reaction.emoji) == constants.YES_VOTE:
                yes_count = reaction.count - 1  # Subtract 1 to exclude bot's reaction
            elif str(reaction.emoji) == constants.NO_VOTE:
                no_count = reaction.count - 1
            elif str(reaction.emoji) == constants.ABSTAIN_VOTE:
                abstain_count = reaction.count - 1

        result_message = f"Vote Results for {proposal_data['title']}:"
        result_message += (
            f"\nAdopt: {yes_count}\nReassess: {no_count}\nAbstain: {abstain_count}"
        )

        logger.info(result_message)

        passed = yes_count > no_count and yes_count >= cfg.YES_COUNT_THRESHOLD

        await message.reply(
            result_message + f"\n\nProposal {'Passed' if passed else 'Failed'}"
        )
        return passed
