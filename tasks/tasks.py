"""
tasks contains the TaskManager class, which contains the check_events and check_concluded_proposals_task functions.
The "check_events" function checks for upcoming events every 50 minutes and posts them to the relevant Discord channel.
The "check_concluded_proposals_task" function checks for concluded proposals every 5 minutes and processes them accordingly.
"""

import time
import discord
import random
from logger.logger import logger
from discord.ext import tasks, commands
from events.event_operations import EventOperations
from utils.utils import Utils
from consts.constants import (
    GENERAL_CHANNEL,
    YES_VOTE,
    NO_VOTE,
    ABSTAIN_VOTE,
    PROPOSAL_CONCLUSION_EMOJIS,
)
import config.config as cfg
from datetime import datetime


class TaskManager:
    @tasks.loop(minutes=5)
    async def check_concluded_proposals_task(bot: commands.Bot):
        """Check for concluded proposals every 5 minutes"""
        try:
            # Get ongoing votes from database
            ongoing_votes = Utils.get_ongoing_votes()
            
            keys_to_remove = []
            for proposal_id, proposal_data in ongoing_votes.items():
                if time.time() < proposal_data["end_time"]:
                    continue

                channel = bot.get_channel(int(proposal_data["channel_id"]))
                if channel:
                    thread = channel.get_thread(int(proposal_data["thread_id"]))
                    if thread:
                        message = await thread.fetch_message(
                            int(proposal_data["message_id"])
                        )
                        if not message:
                            logger.error(
                                f"Unable to find the message with id: {proposal_data['message_id']} in the thread: {thread.id}"
                            )
                            continue
                    else:
                        logger.error(
                            f"Unable to find the thread with id: {proposal_data['thread_id']} in the channel: {channel.name}"
                        )
                        continue
                else:
                    logger.error(
                        f"Unable to find the channel with id: {proposal_data['channel_id']}"
                    )
                    continue
                counts = {
                    YES_VOTE: "yes_count",
                    NO_VOTE: "no_count",
                    ABSTAIN_VOTE: "abstain_count",
                }
                for reaction in message.reactions:
                    emoji = str(reaction.emoji)
                    if emoji in counts:
                        proposal_data[counts[emoji]] = reaction.count - 1
                
                # Update vote counts in database
                Utils.save_ongoing_vote(proposal_id, proposal_data)

                passed = (
                    proposal_data["yes_count"] > proposal_data["no_count"]
                    and proposal_data["yes_count"] >= cfg.YES_COUNT_THRESHOLD
                )
                result_message = (
                    f"Vote for **{proposal_data['title']}** has concluded:\n\n"
                )

                if passed:
                    quorum_value = Utils.fetch_XP_quorum()

                    logger.info(f"Quorum value to be set: {quorum_value}")

                    try:
                        Utils.modify_space_settings(str(quorum_value))
                    except Exception as e:
                        logger.error(f"Error modifying space settings: {e}")
                        continue

                    draft_title = proposal_data["draft"]["title"]
                    proposal_type = proposal_data["draft"]["type"]

                    if proposal_type == "budget":
                        current_budget_id = (
                            cfg.config.getint("ID_START_VALUES", "budget_id") + 1
                        )
                        title = (
                            f"Bloom Budget Proposal #{current_budget_id}: {draft_title}"
                        )
                    elif proposal_type == "governance":
                        current_governance_id = (
                            cfg.config.getint("ID_START_VALUES", "governance_id") + 1
                        )
                        title = f"Bloom General Proposal #{current_governance_id}: {draft_title}"
                    else:
                        logger.error(f"Unknown proposal type: {proposal_type}")
                        continue

                    try:
                        Utils.create_snapshot_proposal(proposal_data, title)
                    except Exception as e:
                        logger.error(f"Error creating snapshot proposal: {e}")
                        continue

                    proposal_url = Utils.fetch_first_open_proposal_url(title)
                    if proposal_url:
                        result_message += f"The vote passes! {random.choice(PROPOSAL_CONCLUSION_EMOJIS)}\n\nSnapshot proposal has been created: **{proposal_url}**"
                        if proposal_type == "budget":
                            cfg.increment_config_id("budget", 1)
                        elif proposal_type == "governance":
                            cfg.increment_config_id("governance", 1)
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
                general_channel = Utils.get_channel_by_name(guild, GENERAL_CHANNEL)

                if general_channel:
                    try:
                        await general_channel.send(result_message)
                    except discord.HTTPException as e:
                        logger.error(
                            f"An error occurred while posting the result message: {e}"
                        )
                else:
                    logger.error(
                        f"Unable to find the general channel in guild: {guild.name}"
                    )

                # Save concluded vote before removing it
                logger.info(f"Saving concluded proposal {proposal_id} to database")
                proposal_data["proposal_id"] = proposal_id
                Utils.save_concluded_vote(
                    proposal_data=proposal_data,
                    passed=passed,
                    snapshot_url=proposal_url if passed else None
                )

                keys_to_remove.append(proposal_id)
                # Remove from database inside the loop
                logger.info(f"Removing concluded proposal {proposal_id} from ongoing votes.")
                Utils.remove_ongoing_vote(proposal_id)

            # Remove from bot's memory
            for key in keys_to_remove:
                bot.ongoing_votes.pop(key)
            
            logger.info(f"Current ongoing_votes: {Utils.get_ongoing_votes()}")
            
        except Exception as e:
            logger.error(f"An error occurred while checking ongoing proposals: {e}")

    @tasks.loop(minutes=2)
    async def check_events(bot: commands.Bot) -> None:
        """
        Task to check for upcoming events every 2 minutes and post them to the relevant Discord channel.
        """
        try:
            if not bot.is_ready():
                return

            # Initialize posted_events if not exists
            if not hasattr(bot, 'posted_events'):
                bot.posted_events = []
                posted_events = Utils.get_posted_events()
                if posted_events:
                    bot.posted_events.extend(posted_events)
                logger.info(f"Initialized posted_events: {bot.posted_events}")

            event_operations = EventOperations(bot)

            current_time = time.time()
            one_hour_ago = current_time - 3600
            logger.info(f"Checking for upcoming events")

            for guild in bot.guilds:
                try:
                    channel = Utils.get_channel_by_name(guild, GENERAL_CHANNEL)
                except ValueError as e:
                    logger.error(f" Cannot check events for guild {guild}, Error: {e}")
                    continue

                upcoming_events = await event_operations.fetch_upcoming_events(guild)

                if not upcoming_events:
                    logger.info(
                        f"No upcoming events in the next 24 hours for guild {guild}."
                    )
                    continue

                notified_events = Utils.get_notified_events()

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
                                f"Skipping event {event.id} as it was recently notified (last notified: {last_notified})"
                            )
                            continue

                        users = event_operations.get_guild_scheduled_event_users(
                            guild.id, event.id
                        )

                        guild_id = event.guild.id
                        user_mentions = [f"<@{user['user_id']}>" for user in users]
                        user_list_string = ", ".join(user_mentions)

                        formatted_event = event_operations.format_event(event, guild_id)
                        
                        # Save the event as posted
                        Utils.save_event(
                            event_id=event.id,
                            guild_id=guild_id,
                            posted_at=current_time
                        )
                        bot.posted_events.append(event.id)

                        if user_list_string:
                            await channel.send(
                                f"🌺 **__Upcoming Event__** 🌺\n{formatted_event}\n\nInterested users: {user_list_string}"
                            )
                        else:
                            await channel.send(
                                f"🌺 **__Upcoming Event__** 🌺\n{formatted_event}"
                            )

                        # Update notified timestamp
                        Utils.save_event(
                            event_id=event.id,
                            guild_id=guild_id,
                            notified_at=current_time
                        )
                else:
                    logger.info(
                        f"No new upcoming events in the next 24 hours for guild {guild}."
                    )
        except Exception as e:
            logger.error(f"Error in check_events loop: {e}")

    @staticmethod
    def start_tasks(bot: commands.Bot):
        """Start all background tasks"""
        TaskManager.check_concluded_proposals_task.start(bot)
        TaskManager.check_events.start(bot)

    async def check_vote_results(self, proposal_data: dict, message: discord.Message) -> bool:
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
        result_message += f"\nAdopt: {yes_count}\nReassess: {no_count}\nAbstain: {abstain_count}"
        
        logger.info(
            f"Vote results for {proposal_data['title']}: "
            f"Yes vote count: {yes_count} No vote count: {no_count} Abstain vote count: {abstain_count}"
        )
        
        # Vote passes if yes > no and meets threshold
        passed = yes_count > no_count and yes_count >= cfg.YES_COUNT_THRESHOLD
        
        await message.reply(result_message + f"\n\nProposal {'Passed' if passed else 'Failed'}")
        return passed
