# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Migration script from JSON file storage to PostgreSQL database
- Added database models for Contributors, Events, OngoingVotes, and ConcludedVotes
- Updated configuration to use environment variables for database credentials
- Added database query script for viewing stored data

## [0.2.1] - 28-2-2024

### Added

- Added previewing for proposals

- Added helper func to calculate quorum requirement, corresponding .js code to update Snapshot space prior to calling proposal submission subprocess

- RPC Fallback and timeout to navigate some client errors that may occur

- handling if optional textInputs are empty

- Added helper function to retrieve snapshot URL to include in a discord announcement & thread for easier access to the live vote.

- Title check to ensure char limit is not exceeded

- Sync of commands outside of on_ready to prevent rate limits from discord.

- Event commands.Cogs.listener/s to cogs/events.py

- helpers directory for helper functions

- Discord Task Decorator that invokes check_ongoing_proposals to see if a proposal has finished.

- Commands reorganized using cogs

- Discord.Embed with colors when using proposal related commands

- Modal for proposal drafting

- / commands instead of using ! or $ prefixes

- Drop down menus for editing, deleting, publishing drafts.

- Check to prevent abuse of specific commands

- on_member_join added to greet a new potential Bloomer, advising them where to start and how to allocate a role to themselves if they are an existing cXP token holder.

- Merged features from OK Bloomer bot.
  - Add to bloomer role, based off an emoji react to a predefined message ID and notify channel
  - Notify channel a person has joined a pod
- Support for both the Bloom Studio Discord server, and the Bloom Collective Discord server.

- Functionality to detect contributors emojis in chat, as well as if their emoji is used as a react. ping the respective user for said emoji.

- Functions to add, remove, or check the contributors that exist

- !bot_help command to provide details about useable comamnds.

- Functionality to list, and delete existing events.

- schedule task that identifies events scheduled to start within the next 24 hours

- Tag interested contributors that an event is started within hte next 24 hours

- Delay between event creation events by 30 minutes to allow for editing of event details before posting to Discord.

- Governance bot to create, edit, and submit proposals to respective governance channels in Discord.

- Restricting governance proposal drafting to one channel in Discord.

- Vote timer to track and identify if a proposal vote passes or fails once published in Discord

- Creating a proposal in Snapshot using the proposal information from Discord

## [0.2.0] - 25-2-2024

- Faulty view 0.2.1

## [0.1.0] - 29-1-2024

- This CHANGELOG file.

[unreleased]: https://github.com/BloomGameStudio/BloomDiscordBot/compare/staging...dev
[0.1.0]: https://github.com/BloomGameStudio/BloomDiscordBot/releases/tag/0.1.0
[0.2.0]: https://github.com/BloomGameStudio/BloomDiscordBot/releases/tag/0.2.0
[0.2.1]: https://github.com/BloomGameStudio/BloomDiscordBot/releases/tag/0.2.1
