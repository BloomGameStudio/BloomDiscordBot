import asyncio
import logging
import subprocess
import config.config as cfg
from shared.constants import GOVERNANCE_BUDGET_CHANNEL_ID, GOVERNANCE_CHANNEL_ID

proposals = []

ongoing_votes = {}

def get_next_governance_id():
    cfg.current_governance_id += 1
    return cfg.current_governance_id

def get_next_budget_id():
    cfg.current_budget_id += 1
    return cfg.current_budget_id

def get_governance_id():
    return cfg.current_governance_id

def get_budget_id():
    return cfg.current_budget_id

async def publish_draft(draft, client):
    if draft["type"].lower() == "budget":
        channel_id = int(GOVERNANCE_BUDGET_CHANNEL_ID)
        current_budget_id = get_next_budget_id()
        cfg.update_id_values(current_budget_id, 'budget')  # Update the budget ID in the config file
        title = f"**Bloom Budget Proposal (BBP) #{current_budget_id}: {draft['name']}**"
    else:
        channel_id = int(GOVERNANCE_CHANNEL_ID)
        current_governance_id = get_next_governance_id()
        cfg.update_id_values(current_governance_id, 'governance')  # Update the governance ID in the config file
        title = f"**Bloom Governance Proposal (BGP) #{current_governance_id}: {draft['name']}**"

    forum_channel = client.get_channel(channel_id)

    if not forum_channel:
        print("Error: Channel not found.")
        return

    # Store the content in a variable
    content = f"""
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

 # Create the thread with the initial message
    thread_with_message = await forum_channel.create_thread(name=title, content=content)
    
    ongoing_votes[thread_with_message.thread.id] = {
        "draft": draft,  # Store the draft info
        "yes_count": 0,  # Initialize counts
        "reassess_count": 0,
        "abstain_count": 0
    }

    # Call the vote_timer function with 4 positional arguments
    await vote_timer(thread_with_message.thread.id, client, channel_id, title, draft)

async def vote_timer(thread_id, client, channel_id, title, draft):
    logging.info(f"Vote timer started for thread_id: {thread_id}, channel_id: {channel_id}, title: {title}")

    # Sleep until the vote ends
    await asyncio.sleep(1 * 60)

    # Fetch the thread again
    channel = client.get_channel(channel_id)
    thread = channel.get_thread(thread_id)

    # Fetch the first message in the thread
    messages = []
    async for message in thread.history(limit=1):
        messages.append(message)

    message = messages[0]

    for reaction in message.reactions:
        
        if str(reaction.emoji) == "👍":
            ongoing_votes[message.id]["yes_count"] = reaction.count
        elif str(reaction.emoji) == "<:bulby_sore:1127463114481356882>":
            ongoing_votes[message.id]["reassess_count"] = reaction.count
        elif str(reaction.emoji) == "<:pepe_angel:1161835636857241733>":
            ongoing_votes[message.id]["abstain_count"] = reaction.count

    logging.info(f"Vote counts for message_id: {message.id} - Yes: {ongoing_votes[message.id]['yes_count']}, Reassess: {ongoing_votes[message.id]['reassess_count']}, Abstain: {ongoing_votes[message.id]['abstain_count']}")

    # Check the result and post it
    result_message = f"Vote for '{title}' has concluded:\n\n"

    if ongoing_votes[message.id]["yes_count"] >= 1:  # Set to quorum needed
        result_message += "The vote passes! :tada:"
        # Call the snapshot creation function
        subprocess.run(['node', './snapshot/wrapper.js', title, draft['abstract'], draft['background'], 'Yes', 'No', 'Abstain'], check=True)
    else:
        result_message += "The vote fails. :disappointed:"

    result_message += f"\n\nYes: {ongoing_votes[message.id]['yes_count']}\nReassess: {ongoing_votes[message.id]['reassess_count']}\nAbstain: {ongoing_votes[message.id]['abstain_count']}"

    await client.get_channel(thread_id).send(result_message)
    logging.info(f"Result message sent to channel_id: {channel_id}")

    # Remove the vote from ongoing_votes
    del ongoing_votes[message.id]
    logging.info(f"Vote for message_id: {message.id} removed from ongoing_votes")