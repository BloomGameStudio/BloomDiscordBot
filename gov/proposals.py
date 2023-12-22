import textwrap
import os
import asyncio
import time
import subprocess
from datetime import timezone, timedelta, datetime
from constants import current_budget_id, current_governance_id

proposals = []

ongoing_votes = {}

def get_next_governance_id():
    global current_governance_id
    current_governance_id += 1
    return current_governance_id

def get_next_budget_id():
    global current_budget_id
    current_budget_id += 1
    return current_budget_id

def get_governance_id():
    return current_governance_id

def get_budget_id():
    return current_budget_id

async def publish_draft(draft, client):
    #Delete?
    channel = None  # Initialize channel with None

    if draft["type"].lower() == "budget":
        #Import and remove os.getenv
        channel_id = int(os.getenv("GOVERNANCE_BUDGET_CHANNEL_ID"))
        current_budget_id = get_next_budget_id()
        title = f"**Bloom Budget Proposal (BBP) #{current_budget_id}: {draft['name']}**"
    else:
        #Same here
        channel_id = int(os.getenv("GOVERNANCE_CHANNEL_ID"))
        current_governance_id = get_next_governance_id()
        title = f"**Bloom Improvement Proposal (BIP) #{current_governance_id}: {draft['name']}**"

    channel = client.get_channel(channel_id)

    if not channel:
        print("Error: Channel not found.")
        return

    if draft["type"].lower() == "budget":
        current_budget_id = get_next_budget_id()
        title = f"**Bloom Budget Proposal (BBP) #{get_budget_id()} {draft['name']}**"
    else:
        current_governance_id = get_next_governance_id()
        title = f"**Topic/Vote {get_governance_id()}: {draft['name']}**"
  
    # Create the message content using the draft information
    msg = f"""
    {title}

    __**Abstract**__
    {draft["abstract"]}

    **__Background__**
    {draft["background"]}

    ** <:inevitable_bloom:1178256658741346344> Yes**
    ** <:bulby_sore:1127463114481356882> Reassess**
    ** <:pepe_angel:1161835636857241733> Abstain**

    Vote will conclude in 48h from now.
    """

    vote_message = await channel.send(textwrap.dedent(msg))

    # Store the vote message ID and relevant information
    ongoing_votes[vote_message.id] = {
        "draft": draft,
        "end_time": asyncio.get_event_loop().time() + 48 * 3600,  # 48 hours in seconds
        "yes_count": 0,
        "reassess_count": 0,
        "abstain_count": 0,
    }

    # Start the timer coroutine
    asyncio.create_task(vote_timer(vote_message.id, client, channel_id, title))

async def vote_timer(message_id, client, channel_id, title):
    # Sleep until the vote ends
    await asyncio.sleep(ongoing_votes[message_id]["end_time"] - asyncio.get_event_loop().time())

    # Count the reactions
    vote_message = await client.get_channel(channel_id).fetch_message(message_id)
    for reaction in vote_message.reactions:
    # Check if the bot's reaction is present (not needed in this case)
    
        if str(reaction.emoji) == "<:inevitable_bloom:1178256658741346344>":
            ongoing_votes[message_id]["yes_count"] = reaction.count
        elif str(reaction.emoji) == "<:bulby_sore:1127463114481356882>":
            ongoing_votes[message_id]["reassess_count"] = reaction.count
        elif str(reaction.emoji) == "<:pepe_angel:1161835636857241733>":
            ongoing_votes[message_id]["abstain_count"] = reaction.count

    # Check the result and post it
    result_message = f"Vote for '{title}' has concluded:\n\n"

    if ongoing_votes[message_id]["yes_count"] >= 5: #Set to qurom needed
        result_message += "The vote passes! :tada:"
        # Call the snapshot creation function
        subprocess.run(['node', './snapshot/wrapper.js', title, ongoing_votes[message_id]['draft']['abstract'], ongoing_votes[message_id]['draft']['background'], 'Yes', 'No', 'Abstain'], check=True)
    else:
        result_message += "The vote fails. :disappointed:"

    result_message += f"\n\nYes: {ongoing_votes[message_id]['yes_count']}\nReassess: {ongoing_votes[message_id]['reassess_count']}\nAbstain: {ongoing_votes[message_id]['abstain_count']}"

    await client.get_channel(channel_id).send(result_message)
    # Remove the vote from ongoing_votes
    del ongoing_votes[message_id]