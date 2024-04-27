"""
tasks module contains the check_events task that is responsible for checking for upcoming events every 60 minutes, and the concluded_proposals_task that is responsible for checking for any proposals that have ended every 5 minutes.
If there are any new events, they are posted to Discord. Interested users are identified and event details are formatted in a message and sent to the general channel.
"""

import time
import subprocess
import discord
import random
from logger.logger import logger
from discord.ext import tasks, commands
from events.event_operations import (
    get_guild_scheduled_event_users,
    save_posted_events,
    fetch_upcoming_events,
)
from helpers import (
    get_channel_by_name,
    update_ongoing_votes_file,
    fetch_first_open_proposal_url,
)
from consts.constants import (
    GENERAL_CHANNEL,
    YES_VOTE,
    NO_VOTE,
    ABSTAIN_VOTE,
    PROPOSAL_CONCLUSION_EMOJIS,
)
from config.config import ONGOING_VOTES_FILE_PATH


@tasks.loop(minutes=60)
async def check_events(bot: commands.Bot) -> None:
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

    Paramaters:
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
                    # Subtract 1 to account for the bot's own reaction
                    proposal_data[counts[emoji]] = reaction.count - 1

            # Check if the proposal has passed based off the yes and no count, and if the yes count is greater than or equal to 5
            if (
                proposal_data["yes_count"] > proposal_data["no_count"]
                and proposal_data["yes_count"] >= 5
            ):
                passed = True
            else:
                passed = False

            # Modify the result message based on the outcome of the vote
            result_message = (
                f"Vote for **{proposal_data['title']}** has concluded:\n\n"
            )
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
                        "Reasses",
                        "Abstain",
                    ],
                    check=True,
                )

                # Call the fetch_first_open_proposal_url after subprocess call
                proposal_url = fetch_first_open_proposal_url()
                if proposal_url:
                    result_message += (
                        f"The vote passes! {random.choice(PROPOSAL_CONCLUSION_EMOJIS)}"
                    )
                else:
                    result_message += (
                        f"The vote passes! {random.choice(PROPOSAL_CONCLUSION_EMOJIS)}"
                    )
            else:
                result_message += "The vote fails. :disappointed:"

            result_message += f"\n**Adopt:** {proposal_data['yes_count']}\nReasses: {proposal_data['no_count']}\nAbstain: {proposal_data['abstain_count']} \n\nSnapshot proposal has been created: **{proposal_url}**"

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
