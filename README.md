# BloomDiscordBot

# Help:

You can type ```$bot_help``` to get details about what commands can be used, along with a brief description of them

# Governance

**Creating proposals:**

Proposals can be drafted by utilizing various commands. 
Upon completing a draft, it will automatically be posted so that you can view / make changes to it prior to publishing it.

When you decide to publish the draft, you can request the bot to do this.

# Commands

The following commands can be used to create, edit, and publish drafts.
All commands start with $. The $ symbol is being used as ! currently conflicts with the existing OK Bloomer bot.

**Vote Draft:**

$vote_draft *or* $v

**Example:**

```$vote_draft``` 

**Response:**

```
Would you like to work on an existing draft or a new one? existing drafts are:
💡 New
```

**Example:**
💡 (react to message)

**Response:**

```
What is the title of this draft?
```

**Example:**

```
Test Budget Draft
```

**Response:**

```
Is this budget or general?
```

**Example:**

```
budget
```

**Response:**

```
Great! What is the abstract?
```

**Example:**

```
This is an example abstract
```

**Response:**

```
Can you provide some background?
```

**Example:**

```
Example background information about the proposal
```

**Response:**

```
Bloom Budget Proposal Draft: Test Budget Draft

Abstract
This is an example abstract

Background
Example background information about the proposal

 :inevitable_bloom: Yes
 :bulby_sore: Reassess
 :pepe_angel: Abstain
 
If you wish to publish your draft proposal, please use command ``$publish_draft``

```

**Edit Draft**

You will use the same command as before ```$vote_draft / $v``` A list of drafts if they exist will appear as a response from the bot. You are required to react to the draft you wish to edit with the 📝 emoji.

**Example:**

```$vote_draft```

**Response:**

```
Would you like to work on an existing draft or a new one? existing drafts are:
📝 Test draft
💡 New
```

**Example:**

```
📝 (react to message)
```

Once you react with the 📝 emoji, the draft you have chosen to edits details will be displayed in a response from the bot.

**Response:**

```
You are editing: Test draft
Draft Details:
Title: Test draft
Abstract: test draft abstract
Background: test draft background
```

You may choose from the following options to edit the title, abstract, and background:

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

**Example:**

```
new title

```

**Response:**

```
You can edit further by repeating the previous step. If you are finished type 'save' without the single quotes
```

To save the draft, type save. The bot will response with the new draft details:

**Example:**

```
save
```

**Response**

```
Topic/Vote 0: new title

Abstract
test draft abstract

Background
test draft background

 :thumbsup: Yes
 :bulby_sore: Reassess
 :pepe_angel: Abstain

If you wish to publish your draft proposal, please use command $publish_draft.
```

**Publish Draft:**

In order to publish a draft you need to use the command $publish_draft [draft name]

This will automatically publish the draft you want to the appropriate Discord channel (Gov-Budget or Governance) depending on if it is a general proposal or a budget.

If / when a published draft reaches qurom, the draft is approved and subsequently posted to Snapshot. NOTE: env vars ``ETH_ADDRESS`` and ``ETH_PRIVATE_KEY``
need to be set.

A Snapshot space is required to be configured and is outside the scope of this documentation. Please refer to https://docs.snapshot.org/ to configure a Snapshot space.

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

 :inevitable_bloom:Yes
 :bulby_sore: Reassess
 :pepe_angel: Abstain

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
All commands start with: $

**List Events:**

```
$list_events
```

**Example:**

```
$list_events
```

**Response:**

```
🗓️ All Events🗓️ 

🌺 Scrutinizer Game night🌺 
event_id: 1180231420476670043
Description: 

🌺 Modular Mesh Architecture🌺 
event_id: 1184322631692980325
Description:
```

**Delete Events:**

```
$delete_event <event_id>
```

**Example**

```
$delete_event 1179242504395165748
```

**Response**

```
Event with ID 1179242504395165748 has been deleted.
```

# Emotes:

When a mapped contributors Emoji is used in Blooms Discord server (as a message, or reaction), the contributor will be DM'd advising they have been mentioned in a chat. A link to the message they have been mentioned in will be included.

# Commands:

The following commands can be used to manage, and list contributors. All commands start with $

**Remove COntributor:**

```
$remove_contributor @contributor
```

**Example:**

```
$remove_contributor @sarahtonein
```

**Response:**

```
Contributor Sarahtonein removed successfully!
```

**Add Contributor:**

```
$add_contributor
```

**Example:**

```
$add_contributor
```

**Response:**

```
 To add a contributor, reply to this message by tagging them with their emoji
    
 **Example:** `@user <:emoji:123456789>`
If you are adding yourself, simply react to this post with your emoji
```

**Example:**

```
@sarahtonein <:sarahtonein>
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
:artifacts: List of Contributors :artifacts:
:gumbo:
:lap:
:balu:
:pizzacat:
:spag:
:baguette:
:breeze:
```