# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
- 
- Governance bot to create, edit, and submit proposals to respective governance channels in Discord.

- Restricting governance proposal drafting to one channel in Discord.

- Vote timer to track and identify if a proposal vote passes or fails once published in Discord

- Creating a proposal in Snapshot using the proposal information from Discord

- This CHANGELOG file.

## [0.1.0] - x-x-2023


[unreleased]: https://github.com/BloomGameStudio/BloomDiscordBot/compare/staging...dev
[0.1.0]: https://github.com/BloomGameStudio/BloomDiscordBot/releases/tag/0.1.0
