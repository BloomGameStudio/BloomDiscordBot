import asyncio
import json
import traceback
import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed
from discord import Member
from discord import Emoji, emoji
from typing import Optional
from domain.contributor import Contributor
from domain.contributor_mention import ContributorMention
from domain.proposal import Proposal
from refactor.proposal_modal import ProposalModal
from refactor.proposal_modal import ProposalButtonsView
from shared.constants import CONTRIBUTORS_FILE_PATH
from shared.constants import GUILD_ID
from discord.ext import commands
from tortoise.expressions import Q

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==================================================
    # ==------------CONTRIBUTOR COMMANDS--------------==
    # ==================================================
    @app_commands.command(name='add_contributor', description="Add a new contributor, also allows you to re-enable old contributors.")
    @app_commands.describe(emoji_string="The emoji to use for this contributor.", contributor="The contributor to tie the emoji to.", user_note="A comment to remind us who this is.")
    async def add_contributor(self, interaction: discord.Interaction, emoji_string:str, contributor:Member, user_note:Optional[str]):
        contributor_object = await Contributor.filter(member_id=interaction.user.id).first()

        if contributor_object is None:
            await interaction.response.send_message("I don't think you're a contributor...?")
            return
        
        response = ""
        print(f"Looking up {contributor.id}")
        contributor_object = Contributor.filter(member_id=contributor.id).first()
        if (contributor_object is None):
            print(f"No contributor object found, creating one.")
            contributor_object = await Contributor.create(
                        member_id=contributor.id,
                        guild_id=GUILD_ID,
                        user_note=user_note,
                        emoji_string = emoji_string,
                        emoji_id=int(emoji_string.split(":", 2)[-1][:-1]),
                        active=True
                )
            response += f"Created a brand new contributor using {emoji_string} and {contributor.mention}.\r\n"
        else:
            print(f"Found existing contributor, updating their emoji.")
            response += "Found existing contributor, updating their emoji and re-activating them if disabled.\r\n"
            try:
                await Contributor.filter(member_id=contributor.id).update(
                    emoji_string=emoji_string,
                    emoji_id = int(emoji_string.split(":", 2)[-1][:-1]),
                    active = True
                )
            except Exception as e:
                await interaction.response.send_message("Invalid input, there was an issue with the emoji parsing most likely.")
                print(f"{'add_contributor', e}")
                print(traceback.format_exc())

        await interaction.response.send_message(f"{response}")

    @app_commands.command(name='remove_contributor')
    @app_commands.describe(emoji_string="The emoji to look up the contributor with.", contributor="The mention of the contributor to move.")
    async def remove_contributor(self, interaction: discord.Interaction, emoji_string:Optional[str], contributor:Optional[Member]):
        contributor_object = await Contributor.filter(member_id=interaction.user.id).first()

        if contributor_object is None:
            await interaction.response.send_message("I don't think you're a contributor...?")
            return
        
        contributor_object = None
        if (emoji_string is not None):
            contributor_object = Contributor.filter(emoji_string=emoji_string).first()
        elif (contributor is not None):
            contributor_object = Contributor.filter(member_id=contributor.id).first()

        if (contributor_object is None):
            await interaction.response.send_message("Could not find contributor by provided input.")

            
        # now we are gauranteed to have an object, either FOUND with filter...
        # or created using create if none was found... now we update the emoji.
        try:
            await Contributor.filter(member_id=contributor.id).update(
                    active = False
                )
            await interaction.response.send_message("Contributor disabled, they won't get DMs anymore.\r\nUse /add_contributor to re-enable.")
        except Exception as e:
            await interaction.response.send_message("Couldn't save changes to contributor.")
            print(f"{'remove_contributor', e}")
            print(traceback.format_exc())

    @app_commands.command(name='list_contributors')
    @app_commands.describe(active_only="If true only fetches active contributors, else fetches all.")
    async def list_contributors(self, interaction: discord.Interaction,  active_only:Optional[bool]):
        contributor_objects = await Contributor.filter(active=(active_only if active_only is not None else True))

        if (len(contributor_objects) == 0):
            await interaction.response.send_message("No contributors found.")
            
        response = ""
        try:
            for c in contributor_objects:
                response += f"{c.emoji_string} - <@{c.member_id}>\r\n"
            e = Embed()
            e.title = f"There are currently {len(contributor_objects)} contributors!"
            e.description = response
            await interaction.response.send_message(embed=e)
        except Exception as e:
            await interaction.response.send_message("Couldn't access contributor data.")
            print(f"{'remove_contributor', e}")
            print(traceback.format_exc())

    @app_commands.command(name='find_mentions')
    @app_commands.describe(n="Finds the most recent n mentions for you, as a contributor.")
    async def find_mentions(self, interaction: discord.Interaction, n:Optional[int]):
        contributor_object = await Contributor.filter(member_id=interaction.user.id).first()

        if contributor_object is None:
            await interaction.response.send_message("I don't think you're a contributor...?")
            return
            
        contributor_mentions = await ContributorMention.filter(contributor=contributor_object)
        if len(contributor_mentions) > 0:
            response = ""
            try:
                for cm in contributor_mentions:
                    try:    
                        msg = await self.bot.get_channel(cm.channel_id).fetch_message(cm.message_id)
                        response += f"<@{cm.member_id}> => {msg.jump_url} @ <t:{round(cm.created_on.timestamp())}:R>\r\n"
                    except Exception as catchall:
                        response += f"<@{cm.member_id}> => <deleted> @ <t:{round(cm.created_on.timestamp())}:R>\r\n"
                e = Embed()
                e.title = f"Your most recent {len(contributor_mentions)} messages."
                e.description = response
                await interaction.response.send_message(embed=e)
            except Exception as e:
                await interaction.response.send_message("Couldn't access contributor data.")
                print(f"{'find_mentions', e}")
                print(traceback.format_exc())
        else:
            await interaction.response.send_message("No mentions found as of yet.")


    # ==================================================
    # ==---------------PROPOSAL COMMANDS--------------==
    # ==================================================
    @app_commands.command(name='find_proposal')
    @app_commands.describe(query="The string to search for amongst proposals.",proposal_id="Pull up a specific proposal by ID (useful when search matches many).")
    async def find_proposal(self, interaction: discord.Interaction, query:str, proposal_id:Optional[int]):
        try:
            proposal_objects = []
            if (proposal_id is None):
                proposal_objects = await Proposal.filter(
                    Q(title__icontains=query) | 
                    Q(background__icontains=query) | 
                    Q(abstract__icontains=query) | 
                    Q(proposal_type__icontains=query)
                )
            else:
                proposal_objects = await Proposal.filter(id=proposal_id)

            if (len(proposal_objects) == 0):
                await interaction.response.send_message(f"No proposals found matching '{query}'.")
            elif(len(proposal_objects) == 1):
                e = Embed()
                e.title = f"Found one matching proposal."
                e.description = f"{proposal_objects[0]}"
                e.footer.text = 'Use the buttons under this embed to publish this draft or edit it.'
                await interaction.response.send_message(embed=e, view=ProposalButtonsView(proposal_objects[0]))
            else:
                response = "***__Found multiple proposals:__***\r\n"
                for p in proposal_objects:
                    response += f"#{p.id} - {p.title}\r\n"
                response += "\r\nPlease use /find_proposal id to pull up one of these specific proposals."
                e = Embed()
                e.title = f"Found {len(proposal_objects)} matching proposals..."
                e.description = response
                await interaction.response.send_message(embed=e, view=EditProposalView(proposal_objects))
        except Exception as e:
            await interaction.response.send_message("Couldn't access proposal data.")
            print(f"{'create_proposal', e}")
            print(traceback.format_exc())
    
    @app_commands.command(name='create_proposal')
    @app_commands.describe(draft="Is this proposal a draft? Default yes.")
    async def create_proposal(self, interaction: discord.Interaction, draft:Optional[bool]):
        try:
            modal = ProposalModal(interaction.channel, None)
            await interaction.response.send_modal(modal) 
            await modal.wait()
            print(f"Proposal created:{modal.proposal}")
        except Exception as e:
            await interaction.response.send_message("Couldn't access proposal data.")
            print(f"{'create_proposal', e}")
            print(traceback.format_exc())
            
    @app_commands.command(name='my_proposals', description="Get a list of all proposals you have made.")
    async def my_proposals(self, interaction: discord.Interaction):
        try:
            proposal_objects = await Proposal.filter(member_id=interaction.user.id)

            if (len(proposal_objects) == 0):
                await interaction.response.send_message(f"No proposals found for {interaction.user.mention}.")
            elif(len(proposal_objects) == 1):
                e = Embed()
                e.title = f"Found one matching proposal."
                e.description = f"{proposal_objects[0]}"
                e.footer.text = 'Use the buttons under this embed to publish this draft or edit it.'
                await interaction.response.send_message(embed=e, view=ProposalButtonsView(proposal_objects[0]))
            else:
                response = "***__Found multiple proposals:__***\r\n"
                for p in proposal_objects:
                    response += f"#{p.id} - {p.title}\r\n"
                response += "\r\nPlease use /find_proposal id to pull up one of these specific proposals."
                e = Embed()
                e.title = f"Found {len(proposal_objects)} matching proposals..."
                e.description = response
                await interaction.response.send_message(embed=e, view=EditProposalView(proposal_objects))
        except Exception as e:
            await interaction.response.send_message("Couldn't access proposal data.")
            print(f"{'create_proposal', e}")
            print(traceback.format_exc())

# ==================================================
# ==---HELPER VIEW CLASSES TO BE EXTERNALIZED-----==
# ==================================================
class EditProposalView(discord.ui.View):
    def __init__(self, proposals):
        super().__init__()
        self.proposals = proposals

    @discord.ui.select(placeholder="Select a proposal to edit?", options=[discord.SelectOption(label="Click here to populate list...",value="Reload")])
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
        print(f"{select.options}")
        print(f"{select.options[0].value}")
        print(f"{select.values[0]}")
        if select.options[0].value != 'Reload':
            p = await Proposal.filter(id=int(select.values[0])).first()
            print(f"{select.options}")
            modal = ProposalModal(interaction.channel, p)
            # Calls the edit modal and passes the correct proposal object.
            await interaction.response.send_modal(modal) 

            # Wait for the user to finish editing...
            await modal.wait()
        else:
            select.options = []
            for proposal in self.proposals:
                select.add_option(label=f"{proposal.proposal_type} #{proposal.id}", description=f"{proposal.title}", value=f"{proposal.id}")
        
        if len(select.options) > 0:
            await interaction.response.edit_message(view=self, embed=interaction.message.embeds[0])
        else:
            await interaction.response.edit_message(view=None, embed=interaction.message.embeds[0], message="The proposal has been edited.")