<div align="center">

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://docs.docker.com/compose/install/)

</div>

# Bloom Discord Bot

A Discord bot that provides core server functionality including contributor notifications and governance utilities.

## Usage
### 🤖 Commands
#### `/contributors`
Return a list of core contributors.

#### `/add_contributor {member} {emoji}`
Add a new member (and associated emoji) to the list of core contributors.

#### `/remove_contributor {member}`
Remove an existing member from the list of core contributors.

#### `/create_proposal {thread_id}`
Create a new proposal from a draft thread. See [🏛️ Proposals](#%EF%B8%8F-proposals) section for more details.

#### `/list_events`
Return a list of upcoming events.

### 😄 Emojis
When a contributor's emoji is used in the server (as a message or reaction), they will be notified of the mention via DM.

### 🏛️ Proposals
To create a new proposal start by creating a new thread in the [#drafting-props](https://discord.com/channels/1152979839737925705/1234677429516111944) channel. Select the appropriate "budget" or "governance" tag. The bot will handle the proposal index based on the selected tag.

Use the appropriate templates for your proposal type:

#### "governance" (general, non-budgetary proposals)
```
**Authors**
Contributors that assisted in drafting the proposal.

**Abstract**
Brief summary of the proposal.

**Definitions**
Definitions for terms that may not be known.

**Details**
Detailed description of the proposal. The goal is to minimize ambiguity.

```

#### "budget" (budgetary proposals)
```
**Authors**
Contributors that assisted in drafting the proposal.

**Abstract**
Brief summary of the proposal.

**Type**
e.g. "Bounty", "Retro-compensation", "RUC"

**Definitions**
Definitions for terms that may not be known.

**Details**
Detailed description of the proposal. The goal is to minimize ambiguity.

**Amount**
Amount & type of token requested.

**Contributors**
Bounty Hunter:
RUC POC:
```
There is a 4000 character limit. You may need to break the proposal up into multiple messages.

**⚠️ Once you have submitted a proposal it cannot be modified for transparency reasons.**

Get the `{thread_id}` value used by the create proposal command from the URL of the draft proposal:
`https://discord.com/channels/{server_id}/{channel_id}/threads/{thread_id}`

## Setup

Make copy of the environment variables file and fill in appropriate values:
```bash
cp .env.example .env
```

## Run
### Docker (recommended)

1. Ensure [Docker](https://docs.docker.com/compose/install/) is installed.
2. Start the containers:
```bash
docker compose up
```

### Local Heroku

1. Ensure [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) is installed.
2. Install dependencies:
```bash
pipenv install --dev
```
3. Run the bot:
```bash
heroku local
```
  