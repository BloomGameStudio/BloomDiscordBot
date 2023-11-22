# BloomDiscordBot


# Emotes:

When a mapped contributors Emoji is used in Blooms Discord server, the contributor will be DM'd advising they have been mentioned in a chat.
A link to the message they have been mentioned in will be included. 

Messages from the bot should only be received during a contributors
hours listed in Notions Team Lookup: https://www.notion.so/bloomgame/38b4e7b631d94dcc969c421742ca76b1?v=5ea223e5b2ec4bf6a1ef58c22a9d3b1c

A contributor can action the DM from the bot to stop being notified.
DM from the bot will be sent on a 4h timer until actioned.

# Commands:

The following commands can be used to manage, and list contributors. All commands 
start with: !

**Remove Contributor:** 

!removecontributor <uid> 

**Example:**

```
!removecontributor 316765092689608706
```

**Response:**
```
Contributor Sarahtonein removed successfully!
```

**Add Contributor:**

!addcontributor

1. !addcontributor

2. Bot will respond with required details.

3. Respond with required details and the contributor will be added.

**Example:**

```
!addcontributor
```
```
To add a contributor, please provide the following information:
Name
User ID (UID)
Emoji ID
UTC Start Time
UTC End Time
Example:Sarahtonein 123456789012345678 <:sarah:1176399164154851368> 1 5

```

**Response:**

```
Contributor Sarahtonein added successfully!
```

**List Contributors:**

!contributors

**Example:**

```
!contributors
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
**Action DM from bot:**

!actioned

**Example**:
```
!actioned
```

**Response:**

```
Thanks for the response! You won't receive any more reminders.
```
