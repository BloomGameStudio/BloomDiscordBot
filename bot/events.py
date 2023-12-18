from discord.ext import commands
from emojis.emojis import emoji_id_mapping, contributors, send_dm_once
import discord
import logging

def setup_events(bot: commands.Bot):
    @bot.event
    async def on_message(message):
        for emoji_id, contributor_uid in emoji_id_mapping.items():
            contributor = next((c for c in contributors if c["uid"] == contributor_uid), None)

            if emoji_id in message.content:
                logging.info('Emoji Found in message!', emoji_id)

                if contributor:
                    try:
                        logging.info(f'Messaging the user, {contributor["uid"]}')
                        message_link = message.jump_url
                        await send_dm_once(bot, contributor, message_link)
                    except discord.errors.NotFound:
                        logging.warning(f'User not found: {contributor["uid"]}')

        if message.author == bot.user:
            return

        await bot.process_commands(message)

    @bot.event
    async def on_reaction_add(reaction, user):
        #Skip reactions from the bot
        if user == bot.user:
            return
        channel = reaction.message.channel

        def check(m):
            # message author == user who added the reaction
            return m.author == user

        contributor_emoji = next(
            (emoji_id for emoji_id, contributor_uid in emoji_id_mapping.items() if str(reaction.emoji) == emoji_id),
        
            None
        )

        if contributor_emoji:
            contributor = next(
                (c for c in contributors if c["uid"] == emoji_id_mapping[contributor_emoji]),
                None
                )

            if contributor:
                message_link = reaction.message.jump_url
                logging.info("Emoji react found, DMing contributor")
                await send_dm_once(bot, contributor, message_link)
