# BloomDiscordBot

# Getting Started:

# Help:

You can type ```$bothelp``` to get details about what commands can be used, along with a brief description of them

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

# Emotes:

When a mapped contributors Emoji is used in Blooms Discord server, the contributor will be DM'd advising they have been mentioned in a chat.
A link to the message they have been mentioned in will be included. 

# Commands:

The following commands can be used to manage, and list contributors. All commands 
start with: $

**Remove Contributor:** 

!removecontributor <uid> 

**Example:**

```
$removecontributor 316765092689608706
```

**Response:**
```
Contributor Sarahtonein removed successfully!
```

**Add Contributor:**
```
$addcontributor
```

```
1. $addcontributor

2. Bot will respond with required details.

3. Respond with required details and the contributor will be added.

```

**Example:**

```
$addcontributor
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