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

Creating a proposal requires careful consideration. Once you have launched a proposal it cannot be modified for transparency reasons. 

Draft your proposal in the Discord Channel [#drafting-props](https://discord.com/channels/1152979839737925705/1234677429516111944). select the appropriate tag [("budget" or "governance")]". The bot will handle the proposal prefix based on the selected tag.

When making a draft, please use the following format for the proposal's body to ensure consistency across proposals.

**Improvement (general governance, non-budgetary proposals)**

- Authors

- Abstract

- Definitions (If applicable)

- Background

- Details (if applicable)

- Implementation Protocol (if applicable)

- Voting Options 
The bot can only use: "Adopt, Reassess, Abstain". These options are to be dynamcially set in the future. 

**Budget (budgetary proposals)**

- Authors

- Abstract

- Type (if applicable)

- Definitions (if applicable)

- Background

- Details (specifics of imbursement, etc)

- Voting Options 
The bot can only use: "Adopt, Reassess, Abstain". These options are to be dynamcially set in the future. 

Upon creating your draft, seek revision from fellow members of Bloom. Once you are happy with your draft and ready for it to be published to Snapshot, use the ```/create_proposal <thread link>``` to begin the Discord voting phase.

If qurom is reached:

```
Vote for 'Bloom Budget Proposal (BBP) #12: Test' has concluded:

The vote passes! :tada:

Yes: 1
Reassess: 0
Abstain: 0
```

Upon passing the Discord phase, the vote will then be published to Snapshot. A 72 hour voting phase begins. At this point, the bot has successfully passed off the handling of the proposal to Snapshot and no longer tracks it.

# Events:

When a bloomer creates an event within Blooms Discord server, there will initially be a 30 minute delay from the time of creation to when the details of the event are posted in Discord. This will allow the bloomer time to make changes to the details, starting time, and so on.

There is a scheduled task that will identify events starting within the next 24 hours. If any are detected those who have expressed interest are informed of the events details in a Discord message.

# Commands:

The following command can be used to list events.

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

In the event that the bot goes down, or there is some other issue with a proposal being pushed to Snapshot, the following steps can be taken. These steps can be done locally, utilizing the test server:

1. Replicate the proposal locally with the bot (Copy / Paste the text & Markdown from the posted proposal in Discord)

2. Create / Publish the proposal by using /vote_draft & /publish_draft locally.

3. Stop the local running of the bot in the test server

4. Use the query_db.py script to verify the proposal data:
```bash
python scripts/query_db.py --table ongoing_votes
```

Example proposal data structure:
```python
{
    "proposal_id": "1232974623113744386",
    "draft": {
        "member_id": 316765092689608706,
        "title": "Annual BVI Services Fee",
        "type": "budget",
        "abstract": "...",
        "background": "...",
        "additional": "..."
    },
    "end_time": 1713962888,
    "title": "Bloom Budget Proposal (BBP) #2: Annual BVI Services Fee",
    "channel_id": "1191283982768287795",
    "thread_id": "1232152965490413630",
    "message_id": "1232152968225357895"
}
```

5. If needed, you can modify the proposal data using the database CLI:
   - Modify `end_time` to any time in the past (48+ hours from when the proposal concluded)
   - Update channel_id to match the correct channel (improvement-props: 1191283932096905307 or budgetary-props: 1191283982768287795)
   - Update `thread_id` and `message_id` to match the Discord thread

6. Build & run the bot

The bot will run the scheduled task check_concluded_proposals_task in 5 minutes time. If all has been done correctly, you should see:
- The concluded message in the bot logs
- The conclusion message under the Discord proposal thread
- The proposal created in Snapshot

## Database Environment Setup

Required environment variables:
- `DB_PASSWORD`: Database password for PostgreSQL
- `ENV`: Set to "DEV" for testing/development

Example `.env`:
```bash
DB_PASSWORD=your_password_here
ENV=DEV
```

The bot connects to PostgreSQL using:
- `DATABASE_URL` if provided (e.g., Heroku's database URL)
- Default URL `postgresql://bloom:{DB_PASSWORD}@localhost:5432/bloombot` if only `DB_PASSWORD` is set

Note: PostgreSQL is required for both development and production environments. Only test suites use SQLite in-memory databases.