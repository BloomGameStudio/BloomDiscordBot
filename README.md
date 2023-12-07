# BloomDiscordBot

# Getting Started:

You will need to set the following environment variables for the bot to function as required:

DISCORD_BOT_TOKEN

GUILD_ID

GENERAL_CHANNEL_ID

GOVERNANCE_TALK_CHANNEL_ID

GOVERNANCE_CHANNEL_ID

GOVERNANCE_BUDGET_CHANNEL_ID

Refer to the .env.example if needed.

Discord.py is used, use pip install discord.py if needed.

Web3 will be used when snapshot is integrated.

# Help Command:

You can type ```$bot_help``` to get details about what commands can be used, along with a brief description of them

# Governance

**Creating proposals:**

Proposals can be drafted by utilizing various commands. 
The drafts will automatically be posted so that you can view / make changes to it prior to posting it.

When you decide to post the draft, you can request the bot to do this.

# Commands

The following commands can be used to create, edit, and publish drafts.
All commands start with $.

**Vote Draft:**

$vote_draft *or* $v

**Example:**

```$vote_draft``` 

**Response:**

```
Would you like to work on an existing draft or a new one? existing drafts are:
💡 New
```

You are then required to react to the message with 💡 to start creating a new draft. You will be prompted to create a title, select a type of proposal (general, or budget) abstract, and finally a background for the proposal.


**Edit Draft**

You will use the same command as before ($vote_draft / $v). A list of drafts if they exist will appear as a response from the bot. You are required to react to the draft you wish to edit with the 📝 emoji.

**Example:**

```$vote_draft```

**Response:**

```
Would you like to work on an existing draft or a new one? existing drafts are:
📝 Test draft
💡 New
```

Once you react with the 📝 emoji, the draft you have chosen to edits details will be displayed in a response from the bot.

```
You are editing: Test draft
Draft Details:
Title: Test draft
Abstract: test draft abstract
Background: test draft background
```

You may choose from the following options to edit the title, abstract, and background respectively:

```
title
abstract
background
```

**Example:**

```
title
```

**Response:**

```
What will be the new title?
```

After entering the amended title, you will get the following response:

```
You can edit further by repeating the previous step. If you are finished type 'save' without the single quotes
```

To save the draft, type save. The bot will response with the new draft details:

```
Topic/Vote 0: new title

Abstract
test draft abstract

Background
test draft background

 :thumbsup: Yes
 :bulby_sore: Reassess
 :pepe_angel: Abstain

Vote will conclude in 48h from now.

If you wish to publish your draft proposal, please use command $publish_draft.
```

**Publish Draft:**

In order to publish a draft you need to use the command $publish_draft [draft name]

This will automatically publish the draft you request to the appropriate Discord channel depending on if it is a general proposal or a budget.

**Example:**

```$publish_draft new title```

**Response:**

```
Publishing draft: new title
Topic/Vote 1: new title

Abstract
new draft abstract

Background
new draft background

 :thumbsup: Yes
 :bulby_sore: Reassess
 :pepe_angel: Abstain

Vote will conclude in 48h from now.
```

# Events:

When a person creates an event within Blooms Discord server, there will initially be a one hour delay from the time of creation to when the details of the event are posted. This will allow the person sometime to make changes to the details, timing and so on.

There is a daily scheduled task that will identify events starting within the next 24 hours. If any are detected everyone is informed of the events details in a Discord message.

Events can also be deleted through a command, detailed below.

# Commands:

The following commands can be used to manage, and list events.
All commands start with: $

**List Events:**

```
$listevents
```

**Example:**

```
$listevents
```

**Response:**

```
All Events:
Event Name: cvbncvbncvbn
Event ID: 1178917740216594432
Event Start Time: November 30, 2023 4:00 PM
Event Description: 
Event Interested: 0
```

**Delete Events:**

```
$deleteevent <event_id>
```

**Example:**

```
$deleteevent 1179242504395165748
```

**Response:**

```
Event with ID 1179242504395165748 has been deleted.
```

# Emojis / Contributor management:

When a mapped contributors Emoji is used in Blooms Discord server, the contributor will be DM'd advising they have been mentioned in a chat.
A link to the message they have been mentioned in will be included. 

# Commands:

The following commands can be used to manage, and list contributors. All commands 
start with: $

**Remove Contributor:** 

$remove_contributor <uid> 

**Example:**

```
$remove_contributor 316765092689608706
```

**Response:**
```
Contributor Sarahtonein removed successfully!
```

**Add Contributor:**
```
$add_contributor
```

```
1. $add_contributor

2. Bot will respond with required details.

3. Respond with required details and the contributor will be added.

```

**Example:**

```
$add_contributor
```

```
To add a contributor, please provide the following information:
Name
User ID (UID)
Emoji ID
Example:Sarahtonein 123456789012345678 <:sarah:1176399164154851368>

```

**Response:**

```
Contributor Sarahtonein added successfully!

```

**List Contributors:**

```
$contributors
```

**Example:**

```
$contributors
```

**Response:**

```
List of Contributors:
Sarahtonein - UID: 316765092689608706
Lapras - UID: 395761182939807744
Balu - UID: 353572599957291010
Pizzacat - UID: 303732860265693185
Spaghetto - UID: 406302927884386318
Baguette - UID: 548974112131776522
Breeze - UID: 154033306894073856
```