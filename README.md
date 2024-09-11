# BloomDiscordBot

# Onboarding Bloomers in the Bloom Studio Server

When a bloomer first joins Bloom Studio's Discord server, they will be welcomed, and encouraged to read and accept the servers rules before they can post. This is a built in anti-spam protection that Discord offers.

After agreeing to the server rules, the bloomer will be able to verify they posses some form of Contributor XP, which upon signing a message through CollabLand will automatically assign the appropriate role to the bloomer

The initial greeting message advise the bloomer where the can get more information about Bloom Studio.

# Bot permissions

The Discord bot has the following permissions:

Integer: 318096215104

Permissions: 

- Manage Roles
- Read Messages / View channels
- Manage Events
- Send Messages
- Create Public Threads
- Send Messages in Threads
- Read Message History
- Mention Everyone
- Add reactions

# Quick start guide:

1. <a name="step1"></a>To run in production mode, set env var "ENV" to "prod". Ensure there are existing channels in Bloom Studio Discord servers with the channel names set in ```constants.py```. The bot will determine the required channel IDs / Forum Channel IDs from the channel names in its respective server.

2. Create a .env file. Reference .env.example for what is required. 

3. To run in dev, reach out to [Sarah](https://github.com/Sarahtonein) for access to the dev server. Alternatively, make your own server, and snapshot space. [Refer to step 1](#step1), and modify ```config/config.ini``` accordingly. The bot **will** default to dev if this env var is not set.

**Docker-Compose**

1. To run the latest version from the main branch:

```
    docker-compose up
```

2. To run and build the checked out branch:

```
    docker-compose up --build
```

**Docker**

1. Create the docker volume for the contributor information / event information

```
    docker volume create bloomdiscordbotvolume
    docker volume create configvolume
```

2. Build the image

```
    //Build with a tag name:
    
    docker build -t bloomdiscordbot .

```

3. Run the container

```
    docker run -d \
        --mount type=volume,source=bloomdiscordbotvolume,target=/app/data \
        --mount type=volume,source=configvolume,target=/app/config \
        bloomdiscordbot

```

OR

```
    //Build without a tag/name prior to running:

    docker build .

    docker run -d \
        --mount type=volume,source=bloomdiscordbotvolume,target=/app/data \
        --mount type=volume,source=configvolume,target=/app/data \
        <image_name>
    
```

# Help:

You can type ```/help``` to get details about what commands can be used, along with a brief description of them

# Governance

**Creating proposals:**

Proposals can be drafted by utilizing various commands. 
Upon completing a draft, it will automatically be posted so that you can view / make changes to it prior to publishing it.

When you decide to publish the draft, you can request the bot to do this.

If you wish to change the emojis used when drafting & reaching soft consensus prior to publishing to snapshot this can be done in consts/constants.py. Simply replace YES_VOTE / NO_VOTE or ABSTAIN_VOTE with the desired emoji id. For example: 

```
YES_VOTE = "<:gunta:1199583728129802322>"
```

# Commands

The following commands can be used to create, edit, and publish drafts.
All commands use discords slash commands (/)

**Vote Draft:**

/vote_draft

**Example:**

```/vote_draft``` 

Upon typing the command, the bot will present you with four buttons: "Create", "Edit", "Preview", and "Delete".

"Create" will create a new proposal.
"Edit" will allow you to select an an existing proposal to edit.
"Preview" will allow you to preview an existing proposal before it is published.
"Delete" will allow you delete and existing proposal that has not been published.

You can use this command repeatedly to perform different actions if necessary.

**Publish Draft:**

In order to publish a draft you need to use the command /publish_draft. 

Select the draft you wish to publish from the dropdown.

This will automatically publish the draft you want to the appropriate Discord channel (Gov-Budget or Governance) depending on if it is a general proposal or a budget.

If / when a published draft reaches qurom, the draft is approved and subsequently posted to Snapshot. NOTE: env vars ``ETH_ADDRESS`` and ``ETH_PRIVATE_KEY``
need to be set.

A Snapshot space is required to be configured and is outside the scope of this documentation. Please refer to https://docs.snapshot.org/ to configure a Snapshot space.

**Example:**

```/publish_draft```

**Posted Response:**

```
Topic/Vote 1: new title

Abstract
new draft abstract

Background
new draft background

 👍 Yes
 👎 Reasses
 ❌ Abstain


Vote will conclude in 48h from now.
```

If qurom is reached:

**Response:**

```
Vote for 'Bloom Budget Proposal (BBP) #12: Test' has concluded:

The vote passes! :tada:

Yes: 1
Reassess: 0
Abstain: 0
```

# Events:

When a bloomer creates an event within Blooms Discord server, there will initially be a 30 minute delay from the time of creation to when the details of the event are posted in Discord. This will allow the bloomer time to make changes to the details, starting time, and so on.

There is a scheduled task that will identify events starting within the next 24 hours. If any are detected those who have expressed interest are informed of the events details in a Discord message.

Events can be deleted through a command, detailed below.

# Commands:

The following commands can be used to delete, and list events.

**List Events:**

```
/list_events
```

**Example:**

```
/list_events
```

**Response:**

```
🗓️ All Events🗓️ 

:link: Event Link https://discord.com/events/1194162649282392125/1207564942220468244 :link:
**Delete Events:**

```

**delete_event:**

```
/delete_event
```

**Example**

```
/delete_event Event_Example
```

**Response**

```
Event with ID Event_Example has been deleted.
```

# Emotes:

When a mapped contributors Emoji is used in Blooms Discord server (as a message, or reaction), the contributor will be DM'd advising they have been mentioned in a chat. A link to the message they have been mentioned in will be included.

# Commands:

The following commands can be used to manage, and list contributors.

**Remove Contributor:**

```
/remove_contributor @contributor
```

**Example:**

```
/remove_contributor @sarahtonein
```

**Response:**

```
Contributor Sarahtonein removed successfully!
```

**Add Contributor:**

```
/add_contributor
```

**Example:**

```
/add_contributor  @sarahtonein :gunta:
```

**Response:**

```
Contributor added successfully!
```

**List Contributors:**

```
/contributors
```

**Example:**

```
/contributors
```

**Response:**

```
:artifacts: List of Contributors :artifacts:
:gumbo:
:lap:
:balu:
:pizzacat:
:spag:
:baguette:
:breeze:
```

# Manually publishing proposals via the bot

In the event that the bot goes down, or there is some other issue with a proposal being pushed to Snapshot, the following steps can be taken. These steps can be done locally, utilizing the test server

1. Replicate the proposal locally with the bot (Copy / Paste the text & Markdown from the posted proposal in Discord)

2. Create / Publish the proposal. by using /vote_draft & /publish_draft locally.

3. Stop the local running of the bot in the test server

4. Access ./data/ongoing_votes.json, copy the proposal object

**Example:**

```

{
    "1232974623113744386": {
        "draft": {
            "member_id": 316765092689608706,
            "title": "Annual BVI Services Fee",
            "type": "budget",
            "abstract": "**Authors**\nSarahtonein\n\n**Type**\nImbursement\n\n**Definitions**\n**British Virgin Islands LTD (BVI LTD):** Refers to a limited liability company formed and registered in the British Virgin Islands.\n\n**Flag Theory:** A strategic framework used for globalizing personal and business operations. The term refers to the service provider engaged by Bloom Studio to assist in the establishment, maintenance, and legal compliance of the BVI LTD.\n\n**EVM Address:** Ethereum Virtual Machine Address. A unique identifier associated with the blockchain wallet used for transactions.\n\n**Abstract**\nThis proposal seeks approval for the annual service fee payment to Flag Theory, essential for the maintenance and compliance of the British Virgin Islands LTD associated with Bloom Studio. The document details the service fee amount and the necessary payment details, providing a basis for members to vote on the continued support of these essential corporate services.",
            "background": "**Background**\nBloom Studio has engaged Flag Theory for the establishment and ongoing maintenance of a corporate entity in the British Virgin Islands (BVI). This strategic partnership ensures compliance with BVI legal and regulatory requirements, which is crucial for maintaining our corporate presence and operational efficiency in the region. To uphold these standards and continue benefiting from Flag Theory's expert services, an annual payment is necessary. This proposal outlines the specifics of the payment and the value derived from this continued collaboration.\n\n**Imbursement Specifics**\n- Amount - $1925\n- EVM Address - 0x9970ff60d7924d4cbaa161c6334fcab9fd859050\n- Invoice details - https://bafybeidujjzbmtiwxhmgpzlxf6bj4gt736vb4ojyhgq6s2qsxkfwew3eie.ipfs.w3s.link/Invoice_INV-7037.pdf",
            "additional": "**Voting Options**\n```\nAdopt\nReassess\nAbstain\n```"
        },
        "end_time": 1713962888,
        "yes_count": 0,
        "title": "Bloom Budget Proposal (BBP) #2: Annual BVI Services Fee",
        "channel_id": "1191283982768287795",
        "thread_id": "1232152965490413630",
        "message_id": "1232152968225357895"
    }
}

```

5. Modify the end_time value so that it is *any* time in the past as long as it is 48+ hours from when the proposal that failed to be published concluded. 

6. Modify channel_id, thread_id, message_id so that it matches the channel ID (improvement-props OR budgetary-props 1191283932096905307 and 1191283982768287795 respectively), thread_id (the thread_id of the thread the discord bot created within the forum channel), and the message_id (the message the bot sent that contains the voting options (yes / reasses / abstain))

7. Modify the BGP / BBP # under the title property, as it will be a default of 0 most likely. Check the Discord thread for the BGP / BBP # if you do not know what number we are up to. 

8. Copy & paste the updated json object into the VM repository ./data/ongoing_votes.json

9. Build & run the bot

The bot should run the scheduled task check_concluded_proposals_task in 5 minutes time, if all has been done correctly you should see the concluded message in the bot logs, and under the thread that has the Discord proposal. You should also see the proposal created in Snapshot. 
