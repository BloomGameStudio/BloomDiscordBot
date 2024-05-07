"""
Tasks module is responsible for running tasks at various intervals.

Specifically: 
- check_events: This task runs every 60 minutes and checks for upcoming events in the next 24 hours.
- check_concluded_proposals_task: This task runs every 5 minutes and checks ongoing proposals to see if they have ended.
- check_snapshot_votes: This task runs every 30 minutes and checks for active proposals on Snapshot.

Refer to each tasks docstring for more information.
"""

import time
import subprocess
import discord
import datetime
import random
from logger.logger import logger
from discord.ext import tasks, commands
from events.event_operations import (
    get_guild_scheduled_event_users,
    save_posted_events,
    fetch_upcoming_events,
)
from helpers.helpers import get_channel_by_name, update_ongoing_votes_file, fetch_first_open_proposal_url, fetch_active_proposals
from consts.constants import GENERAL_CHANNEL, YES_VOTE, NO_VOTE, ABSTAIN_VOTE, PROPOSAL_CONCLUSION_EMOJIS, SNAPSHOT_SPACE, QUORUM_THRESHOLD
from config.config import ONGOING_VOTES_FILE_PATH

sent_reminders = {}

@tasks.loop(minutes=60)
async def check_events(bot: commands.Bot) -> None:
    """
    This function is a task that runs every 60 minutes. It checks for upcoming events in the next 24 hours.
    If there are upcoming events, it will post a message in the general channel of the guild.

    Parameters:
    bot (commands.Bot): The bot instance containing the posted_events attribute.

    Returns:
    None
    """
    if not bot.is_ready():
        return

    for guild in bot.guilds:
        try:
            channel = get_channel_by_name(guild, GENERAL_CHANNEL)
        except ValueError as e:
            logger.error(f" Cannot check events for guild {guild}, Error: {e}")
            continue

        upcoming_events = await fetch_upcoming_events(guild)

        if not upcoming_events:
            logger.info(f"No upcoming events in the next 24 hours for guild {guild}.")
            continue

        new_events = [
            event for event in upcoming_events if event.id not in bot.posted_events
        ]

        if new_events:
            for event in new_events:
                users = get_guild_scheduled_event_users(guild.id, event.id)

                guild_id = event.guild.id
                user_mentions = [f"<@{user['user_id']}>" for user in users]
                user_list_string = ", ".join(user_mentions)

                formatted_string = (
                    f"📆 **Upcoming Events in the Next 24 Hours** 📆 \n"
                    f"\n"
                    f":link: **Event Link https://discord.com/events/{guild_id}/{event.id} :link:**\n"
                    f"\n"
                    f"{user_list_string}\n"
                )

                await channel.send(formatted_string)
                bot.posted_events.append(event.id)
                save_posted_events(bot.posted_events)
        else:
            logger.info(
                f"No new upcoming events in the next 24 hours for guild {guild}."
            )


@tasks.loop(minutes=5)
async def check_concluded_proposals_task(bot: commands.Bot):
    """
    This function is a task that runs every 5 minutes. It checks ongoing proposals and processes them if they have ended.
    If a proposal has ended, and meets the criteria of passing, a snapshot proposal will be created.

    Parameters:
    bot (commands.Bot): The bot instance containing the ongoing_votes attribute.

    Returns:
    None
    """
    if not bot.is_ready():
        return

    logger.info("Checking to see if proposals have ended")
    try:
        keys_to_remove = []  # Initialize list to store keys for removal

        for proposal_id, proposal_data in bot.ongoing_votes.items():
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
                    # Subtract 1 to account for the bots reaction
                    proposal_data[counts[emoji]] = reaction.count - 1

            # Check if the proposal has passed based off the yes and no count, and if the yes count is great than or equal to 5
            passed = proposal_data["yes_count"] > proposal_data["no_count"] and proposal_data["yes_count"] >= 5
            result_message = f"Vote for **{proposal_data['title']}** has concluded:\n\n"

            if passed:
                subprocess.run(
                    [
                        "node",
                        "./snapshot/wrapper.js",
                        proposal_data["title"],
                        proposal_data["draft"]["abstract"],
                        proposal_data["draft"]["background"],
                        proposal_data["draft"]["additional"],
                        "Adopt",
                        "Reassess",
                        "Abstain",
                    ],
                    check=True,
                )
                # Call the fetch_first_open_proposal_url after subprocess call
                proposal_url = fetch_first_open_proposal_url(proposal_data["title"])
                if proposal_url:
                    result_message += f"The vote passes! {random.choice(PROPOSAL_CONCLUSION_EMOJIS)}\n\nSnapshot proposal has been created: **{proposal_url}**"
                else:
                    result_message += f"The vote passes! {random.choice(PROPOSAL_CONCLUSION_EMOJIS)}"
            else:
                result_message += "The vote fails. :disappointed:"

            result_message += f"\nAdopt: {proposal_data['yes_count']}\nReasses: {proposal_data['no_count']}\nAbstain: {proposal_data['abstain_count']}"

            logger.info(
                f"Yes vote count: {proposal_data['yes_count']} No vote count: {proposal_data['no_count']} Abstain vote count: {proposal_data['abstain_count']}"
            )

            # Post the result message to the corresponding thread
            try:
                await thread.send(result_message)
            except discord.HTTPException as e:
                logger.error(f"An error occurred while posting the result message: {e}")

            guild = channel.guild
            general_channel = get_channel_by_name(guild, GENERAL_CHANNEL)

            if general_channel:
                try:
                    await general_channel.send(result_message)
                except discord.HTTPException as e:
                    logger.error(f"An error occurred while posting the result message: {e}")
            else:
                logger.error(f"Unable to find the general channel in guild: {guild.name}")

            keys_to_remove.append(proposal_id)

        # Remove concluded votes
        for key in keys_to_remove:
            bot.ongoing_votes.pop(key)

        update_ongoing_votes_file(bot.ongoing_votes, ONGOING_VOTES_FILE_PATH)

    except Exception as e:
        logger.error(f"An error occurred while checking ongoing proposals: {e}")

@tasks.loop(minutes=20)
async def check_snapshot_votes(bot: commands.Bot):
    """
    Checks for active proposals on Snapshot and sends reminders in specific guild when there are 24 and 12 hours left.
    
    Parameters:
    bot (commands.Bot): The bot instance
    
    Returns:
    None
    """
    if not bot.is_ready():
        logger.info("Bot is not ready.")
        return
    
    logger.info("Checking for active proposals on Snapshot")
    proposals = fetch_active_proposals()

    if proposals:
        now = datetime.datetime.now(datetime.timezone.utc)

        for guild in bot.guilds:
            if guild.name == "Bloom Studio":
                try:
                    channel = get_channel_by_name(guild, GENERAL_CHANNEL)
                except ValueError as e:
                    logger.error(f"Cannot check snapshot votes for guild {guild}, Error: {e}")
                    continue  # Continue to check next guild if any

                for proposal in proposals:
                    proposal_id = proposal['id']
                    end_val = proposal.get('end')
                    if isinstance(end_val, int):
                        end_time = datetime.datetime.fromtimestamp(end_val, datetime.timezone.utc)
                        remaining = (end_time - now).total_seconds() / 60  # Calculate remaining time in minutes
                        total_votes = proposal.get('scores_total', 0)
                        proposal_url = f"https://snapshot.org/#{SNAPSHOT_SPACE}/proposal/{proposal_id}"

                        if proposal_id not in sent_reminders:
                            sent_reminders[proposal_id] = set()

                        if total_votes < QUORUM_THRESHOLD:
                            if 1380 <= remaining <= 1500 and '24_hour' not in sent_reminders[proposal_id]:  # Check for 24 hour reminder
                                await channel.send(f"**Reminder** :hourglass: @here Only 24 hours left to vote on **{proposal['title']}**. \n\n**Cast your vote:** {proposal_url}")
                                sent_reminders[proposal_id].add('24_hour')
                            if 690 <= remaining <= 750 and '12_hour' not in sent_reminders[proposal_id]:  # Check for 12 hour reminder
                                await channel.send(f"**Reminder** :hourglass_flowing_sand: @here Only 12 hours left to vote on **{proposal['title']}**. \n\n**Cast your vote:** {proposal_url}")
                                sent_reminders[proposal_id].add('12_hour')