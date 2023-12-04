# BloomDiscordBot

**Creating proposals:**

Proposals can be drafted by utilizing various commands. 
The drafts will automatically be posted so that you can view / make changes to it prior to posting it.

When you decide to post the draft, they can request the bot to do this.

**Commands:**

The following commands can be used to creat, edit, and publish drafts.
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