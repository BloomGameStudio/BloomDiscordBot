import asyncio
import subprocess
import config.config as cfg
from shared.constants import GOVERNANCE_BUDGET_CHANNEL_ID, GOVERNANCE_CHANNEL_ID

proposals = []

ongoing_votes = {}

# Upon publishing a draft, get the current ID and increment it by 1
# Then update the config file with the current ID
async def publish_draft(draft, client):
    if draft["type"].lower() == "budget":
        id_type = 'budget'
        channel_id = int(GOVERNANCE_BUDGET_CHANNEL_ID)
    else:
        id_type = 'governance'
        channel_id = int(GOVERNANCE_CHANNEL_ID)

    if id_type == 'budget':
        cfg.current_budget_id += 1
        cfg.update_id_values(cfg.current_budget_id, id_type)  # Update the budget ID in the config file
        title = f"**Bloom Budget Proposal (BBP) #{cfg.current_budget_id}: {draft['name']}**"
    else:
        cfg.current_governance_id += 1
        cfg.update_id_values(cfg.current_governance_id, id_type)  # Update the governance ID in the config file
        title = f"**Bloom Governance Proposal (BGP) #{cfg.current_governance_id}: {draft['name']}**"
    
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

    await vote_timer(thread_with_message.thread.id, client, channel_id, title, draft)

async def vote_timer(thread_id, client, channel_id, title, draft):

    # Sleep until the vote ends
    await asyncio.sleep(48 * 3600)

    # Fetch the thread again
    channel = client.get_channel(channel_id)
    thread = channel.get_thread(thread_id)

    # Fetch the first message in the thread
    messages = []
    async for message in thread.history(limit=1):
        messages.append(message)

    message = messages[0]

    for reaction in message.reactions:
        
        if str(reaction.emoji) == "<:inevitable_bloom:1192384857691656212>":
            ongoing_votes[message.id]["yes_count"] = reaction.count
        elif str(reaction.emoji) == "<:bulby_sore:1127463114481356882>":
            ongoing_votes[message.id]["reassess_count"] = reaction.count
        elif str(reaction.emoji) == "<:pepe_angel:1161835636857241733>":
            ongoing_votes[message.id]["abstain_count"] = reaction.count

    # Check the result and post it
    result_message = f"Vote for '{title}' has concluded:\n\n"

    if ongoing_votes[message.id]["yes_count"] >= 5:  # Set to quorum needed
        result_message += "The vote passes! :tada:, snapshot proposal will now be created"
        # Call the snapshot creation function
        subprocess.run(['node', './snapshot/wrapper.js', title, draft['abstract'], draft['background'], 'Yes', 'No', 'Abstain'], check=True)
    else:
        result_message += "The vote fails. :disappointed:"

    result_message += f"\n\nYes: {ongoing_votes[message.id]['yes_count']}\nReassess: {ongoing_votes[message.id]['reassess_count']}\nAbstain: {ongoing_votes[message.id]['abstain_count']}"

    await client.get_channel(thread_id).send(result_message)

    # Remove the vote from ongoing_votes
    del ongoing_votes[message.id]