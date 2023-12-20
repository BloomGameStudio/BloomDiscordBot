from emotes.command_operations import send_dm_once
import discord
import logging

async def handle_message(bot, message, contributors, emoji_id_mapping):
    if message.author == bot.user:
        return

    for emoji_id, contributor_uid in emoji_id_mapping.items():
        contributor = None
        for c in contributors:
            if c["uid"] == contributor_uid:
                contributor = c
                break

        if emoji_id in message.content:
            logging.info('Emoji Found in message!', emoji_id)

            if contributor:
                try:
                    logging.info(f'Messaging the user, {contributor["uid"]}')
                    message_link = message.jump_url
                    await send_dm_once(bot, contributor, message_link)
                except discord.errors.NotFound:
                    logging.warning(f'User not found: {contributor["uid"]}')

    await bot.process_commands(message)

async def handle_reaction(bot, reaction, user, contributors, emoji_id_mapping):
    if user == bot.user:
        return

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