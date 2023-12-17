import os
import logging
from discord.ext import tasks, commands

def setup_tasks(bot: commands.Bot):
    @tasks.loop(minutes=59)
    async def daily_check_events():
        guild_id = int(os.getenv("GUILD_ID"))
        guild = bot.get_guild(guild_id)

        if guild:
            event_list = await check_upcoming_events(guild, time_range=24 * 3600)

            if not event_list:
                logging.info("No upcoming events in the next 24 hours.")
                return

            channel_id = int(os.getenv("GENERAL_CHANNEL_ID"))
            channel = guild.get_channel(channel_id)

            if not channel:
                logging.warning("Event channel not found")
                return

            # Common message part
            common_message = f"<:inevitable_bloom:1178256658741346344> **Upcoming Events in the Next 24 Hours** <:inevitable_bloom:1178256658741346344> \n"

            # Load posted events
            posted_events = load_posted_events()

            # Check if it's the initial run or not
            if not posted_events:
                # Initial run, post events to Discord
                for event in event_list:
                    # Fetch subscribed users for each event
                    users = get_guild_scheduled_event_users(guild_id, event.id)
                    user_mentions = [f"<@{user['user_id']}>" for user in users]
                    user_list_string = ', '.join(user_mentions)

                    formatted_string = (
                        f"\n"
                        f"{common_message}\n"
                        f":link: **Event Link https://discord.com/events/{guild_id}/{event.id} :link:**\n"
                        f"\n"
                        f"{user_list_string}\n"
                    )

                    # Send message
                    await channel.send(formatted_string)

                save_posted_events([event.id for event in event_list])
            else:
                # Subsequent runs, filter out already posted events
                new_events = [event for event in event_list if event.id not in posted_events]

                if new_events:
                    for event in new_events:
                        # Fetch subscribed users for each event
                        users = get_guild_scheduled_event_users(guild_id, event.id)
                        user_mentions = [f"<@{user['user_id']}>" for user in users]
                        user_list_string = ', '.join(user_mentions)

                        formatted_string = (
                            f"{common_message}\n"
                            f":link: **Event Link https://discord.com/events/{guild_id}/{event.id} :link:**\n"
                            f"\n"
                            f"{user_list_string}\n"
                        )

                        # Send message
                        await channel.send(formatted_string)

                    # Update the posted_events list only for newly posted events
                    posted_events.extend([event.id for event in new_events])
                    save_posted_events(posted_events)
                else:
                    logging.info("No new upcoming events in the next 24 hours.")
        else:
            logging.warning("Guild not found")

    daily_check_events.start()