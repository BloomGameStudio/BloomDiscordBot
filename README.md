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

1. Ensure there are existing channels in Bloom Collective, and Bloom Studio Discord servers with the channel names set in constants.py. The bot will determine the required channel IDs / Forum Channel IDs from the channel names in it's respective server.

2. Create a .env file. Reference .env.example for what is required. 

3. Set the proposal parameters and space settings to be used in ./snapshot/snapshot.js. For example:

```
    const proposalParams = {
      space: 'bloomtest.eth', // Set the space
      type: 'weighted', // Define the voting system
      title: removeMarkdown(title),
      body: `Abstract:\n ${removeMarkdown(abstract)}\n\n Background:\n ${removeMarkdown(background)}`,
      choices: choices.map(removeMarkdown),
      start: currentTime,
      end: currentTime + fortyeighthoursinSeconds,
      snapshot: await provider.getBlockNumber(), 
      network: '1',
      plugins: JSON.stringify({}),
      app: 'Gov-test' // provide the name of your project using this Snapshot.js integration
    };
```

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

Upon typing the command the bot will present you with three buttons: Create, Edit, Delete.

These should be self explained, create will allow you to draft a proposal. Edit will allow you to edit an existing proposal, and delete
will let you delete an existing proposal that has not yet been published. 

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
/delete_event <name>
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