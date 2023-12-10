import discord
import os
import asyncio
from datetime import datetime, timezone, timedelta
from discord.ext import commands, tasks
from emojis.emojis import emoji_id_mapping, contributors, send_dm_once, update_json_file, add_contributor
from updates.updates import check_upcoming_events, load_dotenv, notify_new_event, format_event
from gov.proposals import proposals, new_proposal_emoji, publish_draft, get_governance_id, textwrap, get_budget_id

#Load ENV

load_dotenv()

#Discord Config

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="$", intents=intents)

#Bot events

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Watching you sleep"))

    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emojis'))
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        await check_upcoming_events(guild)
        # Start the background task to check events automatically every 24 hours
        daily_check_events.start()
    else:
        print(f"Guild not found")
    
@bot.event
async def on_message(message):
    for emoji_id, contributor_uid in emoji_id_mapping.items():
        contributor = next((c for c in contributors if c["uid"].lower() == contributor_uid.lower()), None)

        if emoji_id in message.content:
            print(f'Emoji Found in message!', emoji_id)
            
            if contributor:
                print(f'Messaging the user, {contributor["uid"]}')
                message_link = message.jump_url
                await send_dm_once(bot, contributor, message_link)

    fmt_proposals = ""

    # Loop over proposals and convert them to str with every proposal name being on a newline
    for proposal in proposals:
        fmt_proposals += f"📝 {proposal['name']}\n"

    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.event
async def on_scheduled_event_create(event):
    print(f"New scheduled event created: {event.name}")
    await notify_new_event(bot, event)

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
            (c for c in contributors if c["uid"].lower() == emoji_id_mapping[contributor_emoji].lower()),
            None
        )

        if contributor:
            message_link = reaction.message.jump_url
            await send_dm_once(bot, contributor, message_link)

    elif reaction.emoji == "📝":
        # Find/Get proposal that the user wants to edit or None
        edit_proposal = next(
            (
                item
                for item in proposals
                if (
                    reaction.message.content.strip().endswith(item["name"].strip())
                )  # In case of conflicts use == comparison after removing emoji and whitespace
            ),
            None,
        )

        if edit_proposal:
            await reaction.message.channel.send(f"You are editing: {edit_proposal['name']}")
            await reaction.message.channel.send("**Draft Details:**\n"
                                       f"**Title:** {edit_proposal['name']}\n"
                                       f"**Abstract:** {edit_proposal['abstract']}\n"
                                       f"**Background:** {edit_proposal['background']}\n")

            change_selection = await bot.wait_for("message", check=check)
            change_selection = change_selection.content.lower()

            while True:
                if change_selection == "title":
                    await channel.send("What will be the new title?")
                    change_answer = await bot.wait_for("message", check=check)
                    edit_proposal["name"] = change_answer.content

                if change_selection == "type":
                    await channel.send("What will be the new type?")
                    change_answer = await bot.wait_for("message", check=check)
                    edit_proposal["type"] = change_answer.content

                if change_selection == "abstract":
                    await channel.send("What will be the new abstract?")
                    change_answer = await bot.wait_for("message", check=check)
                    edit_proposal["abstract"] = change_answer.content

                if change_selection == "background":
                    await channel.send("What will be the new background?")
                    change_answer = await bot.wait_for("message", check=check)
                    edit_proposal["background"] = change_answer.content

                await channel.send(
                    "You can edit further by repeating the previous step. If you are finished type 'save' without the single quotes"
                )

                change_selection = await bot.wait_for("message", check=check)
                change_selection = change_selection.content.lower()

                if change_selection.lower() == "save":
                    await channel.send("Changes have been saved")

                    if edit_proposal["type"].lower() == "budget":
                        title = f"**Bloom Budget Proposal (BBP) #{get_budget_id()} {edit_proposal['name']}**"
                    else:
                        title = f"**Topic/Vote {get_governance_id()}: {edit_proposal['name']}**"

                    end_time = datetime.utcnow() + timedelta(hours=48)

                    formatted_end_time = end_time.strftime('<t:%s:f>' % str(int(end_time.timestamp())))

                    msg = f"""
                    {title}

                    __**Abstract**__
                    {edit_proposal["abstract"]}

                    **__Background__**
                    {edit_proposal["background"]}

                    ** <a:rave_kirby:1161841544291164252> Yes**
                    ** <:bulby_sore:1127463114481356882> Reassess**
                    ** <:pepe_angel:1161835636857241733> Abstain**

                    Vote will conclude at {formatted_end_time}. \n
                    If you wish to publish your draft proposal, please use command ``$publish_draft``.
                    """

                    await channel.send(textwrap.dedent(msg))

                    break

                elif change_selection.lower() == "cancel":
                    await channel.send("Editing has been cancelled")
                    break
        else:
            await channel.send("Draft not found")

    elif reaction.emoji == new_proposal_emoji:
        await reaction.message.channel.send("What is the title of this draft?")

        proposal = {}

        name = await bot.wait_for("message", check=check)
        proposal["name"] = name.content
        proposals.append(proposal)

        await channel.send("Is this budget or general?")

        type = await bot.wait_for("message", check=check)
        proposal["type"] = type.content

        await channel.send(f"Great! What is the abstract?")

        abstract = await bot.wait_for("message", check=check)
        proposal["abstract"] = abstract.content

        await channel.send("Can you provide some background?")

        background = await bot.wait_for("message", check=check)
        proposal["background"] = background.content

        if proposal["type"].lower() == "budget":
            title = f"**Bloom Budget Proposal (BBP) #{get_budget_id()} {name.content}**"
       
        else:
            title = f"**Topic/Vote {get_governance_id()}: {name.content}**"

        end_time = datetime.utcnow() + timedelta(hours=48)

        formatted_end_time = end_time.strftime('<t:%s:f>' % str(int(end_time.timestamp())))

        msg = f"""
        {title}

        __**Abstract**__
        {abstract.content}

        **__Background__**
        {background.content}

        ** <a:rave_kirby:1161841544291164252> Yes**
        ** <:bulby_sore:1127463114481356882> Reassess**
        ** <:pepe_angel:1161835636857241733> Abstain**

        Vote will conclude at {formatted_end_time} . \n
        If you wish to publish your draft proposal, please use command ``$publish_draft``
        """

        await channel.send(textwrap.dedent(msg))

#Bot commands

@bot.command(name='vote_draft', aliases=['v'], pass_context=True)
async def votedraft(ctx):

    if ctx.channel.id != int(os.getenv('GOVERNANCE_TALK_CHANNEL_ID')):
        await ctx.send("This command can only be used in the Governance talk channel")
        return
    msg = "Would you like to work on an existing draft or a new one? Existing drafts are:"

    await ctx.send(msg)

    for proposal in proposals:
        await ctx.send(f"📝 {proposal['name']}")

    await ctx.send(f"{new_proposal_emoji} New")

@bot.command(name='publish_draft')
async def publishdraft(ctx, *, draft_name):
    draft_to_publish = next(
        (item for item in proposals if item["name"].strip() == draft_name.strip()),
        None,
    )

    if draft_to_publish:
        await ctx.send(f"Publishing draft: {draft_to_publish['name']}")
        await publish_draft(draft_to_publish, bot)
        proposals.remove(draft_to_publish)
    else:
        await ctx.send(f"Draft not found: {draft_name}")

@bot.command(name='contributors')
async def listcontributors(ctx):
    contributors_list = "\n".join([f"{contributor['name']} - UID: {contributor['uid']}" for contributor in contributors])
    await ctx.send("<:artifacts:1113725319011110943> **List of Contributors** <:artifacts:1113725319011110943>\n" + contributors_list)

@bot.command(name='remove_contributor')
async def removecontributor(ctx, uid_to_remove=None):
    if uid_to_remove:
        for contributor in contributors:
            if contributor["uid"] == uid_to_remove:
                emoji_id_to_remove = next((emoji_id for emoji_id, c in emoji_id_mapping.items() if c == contributor), None)
                if emoji_id_to_remove:
                    del emoji_id_mapping[emoji_id_to_remove]
                contributors.remove(contributor)
                update_json_file()
                print(f"Contributor {contributor['name']} removed successfully!")
                await ctx.send(f"Contributor {contributor['name']} removed successfully!")
                return
        await ctx.send("Contributor not found.")
    else:
        await ctx.send("Please provide the UID of the contributor to remove.")

@bot.command(name='add_contributor')
async def addcontributor(ctx):
    ctx.channel

    await ctx.send("**To add a contributor, provide the following information:**\n"
                   "\n"
                   "**1. Name**\n"
                   "**2. User ID (UID)**\n"
                   "**3. Emoji ID**\n"
                   "**Example:** `Sarahtonein 123456789012345678 <:sarah:123456789>`")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        response = await bot.wait_for('message', check=check, timeout=60)
        inputs = response.content.split()
        if len(inputs) == 3:
            name, uid, emoji_id = inputs

            # Check if the UID already exists in contributors
            existing_contributor = next((c for c in contributors if c["uid"].lower() == uid.lower()), None)

            if existing_contributor:
                print(f'Contributor {existing_contributor["name"]} already exists')
                await ctx.send(f"Contributor {existing_contributor['name']} already exists")
            else:
                # UID doesn't exist, call add_contributor
                new_contributor = add_contributor(name, uid, emoji_id)
                print(f'New contributor added:', name, uid)
                await ctx.send(f"Contributor {new_contributor['name']} added successfully!")
        else:
            await ctx.send("Invalid input. Please provide all required information.")
    except asyncio.TimeoutError:
        await ctx.send("Timeout. Please run the command again.")

@bot.command(name='list_events')
async def listevents(ctx):
    guild = ctx.guild
    event_list = await check_upcoming_events(guild)
    formatted_events = [format_event(event) for event in event_list]
    formatted_string = "\n\n".join(formatted_events)

    await ctx.send(f"🗓️**All Events**🗓️\n{formatted_string}")

@bot.command(name='delete_event')
async def deleteevent(ctx, event_id: int = None):
    if event_id is None:
        await ctx.send("Please enter an event_id with this command. Example: `$deleteevent 1179241076016566272`")
        return

    guild = ctx.guild

    try:
        event_id = int(event_id)
    except ValueError:
        await ctx.send("Invalid event_id. Please provide a valid integer. Use $listevents to get a list of events")
        return

    event = guild.get_scheduled_event(event_id)

    if event:
        # Delete the event
        await event.delete()
        await ctx.send(f"Event with ID {event_id} has been deleted 🗑️")
    else:
        await ctx.send(f"No event found with ID {event_id}.")

@bot.command(name='bot_help')
async def help_command(ctx):
    help_message = (
        "**Here are the available commands this bot supports:**\n\n"
        "```\n"
        "$list_events: List all upcoming events.\n"
        "```\n"
        "```\n"
        "$delete_event [event_id]: Delete an event with the specified ID.\n"
        "```\n"
        "```\n"
        "$contributors: List all stored contributors, Name, UID.\n"
        "```\n"
        "```\n"
        "$add_contributor: Allows you to add a contributor to stored contributors\n"
        "  you provide the following after the bot responds: name, UID, EmojiID\n"
        "```\n"
        "```\n"
        "$remove_contributor: Allows you to remove a contributor; you must provide a contributor's UID with this command\n"
        "```\n"
        "```\n"
        "$publish_draft: Allows you to publish a draft and start a vote coutdown."
        "```\n"
        "```\n"
        "$v or $vote_draft: Ällows you to start drafting a proposal. These can be edited by using the same command and reacting with 📝"
        "```\n"
        "```\n"
        "$bot_help: This will give you the list of commands available.\n"
        "```\n"
        "This bot will also DM contributors if you react to a message with their respective emoji, or include it in a message"
    )

    await ctx.send(help_message)

#Bot tasks

# This may have its own issues if the bot is restarted
@tasks.loop(hours=24)
async def daily_check_events():
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        event_list = await check_upcoming_events(guild, time_range=24 * 3600)

        if event_list:
            formatted_events = [format_event(event) for event in event_list]
            formatted_string = "\n\n".join(formatted_events)

            channel_id = int(os.getenv("GENERAL_CHANNEL_ID"))
            channel = guild.get_channel(channel_id)

            if channel:
                # Tag @here and send the message
                await channel.send(f"<:inevitable_bloom:1178256658741346344> **Upcoming Events in the Next 24 Hours - here** <:inevitable_bloom:1178256658741346344> \n{formatted_string}")
            else:
                print(f"Event channel not found")
        else:
            print("No upcoming events in the next 24 hours.")
    else:
        print(f"Guild not found")

bot.run(os.getenv('DISCORD_BOT_TOKEN'))