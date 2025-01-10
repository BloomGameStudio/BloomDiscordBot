from typing import Dict, Any, List
import discord
from discord.ext import commands
import re
import logging

logger = logging.getLogger(__name__)

class ProposalSection:
    """Represents a section of a proposal with its content"""
    def __init__(self, name: str, content: str = ""):
        self.name = name
        self.content = content

class ThreadParser:
    KNOWN_SECTIONS = [
        "Authors",
        "Abstract",
        "Definitions",
        "Background",
        "Details",
        "Implementation Protocol",
        "Voting Options"
    ]

    @staticmethod
    def extract_thread_id(thread_input: str) -> int:
        """Extract thread ID from either a URL or direct ID"""
        try:
            if 'discord.com' in thread_input:
                thread_id = int(thread_input.split('/')[-1])
            else:
                thread_id = int(thread_input.strip())
            return thread_id
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid thread ID or URL format: {e}")

    @staticmethod
    async def fetch_thread(bot: commands.Bot, thread_id: int) -> discord.Thread:
        """Fetch thread with error handling and logging"""
        try:
            thread = await bot.fetch_channel(thread_id)
            
            if not isinstance(thread, discord.Thread):
                raise ValueError("Channel is not a thread")
                
            return thread
            
        except discord.NotFound:
            logger.error(f"Thread {thread_id} not found")
            raise ValueError(f"Thread {thread_id} not found")
        except discord.Forbidden:
            logger.error(f"Bot lacks permissions to access thread {thread_id}")
            raise ValueError("Bot lacks permissions to access this thread")
        except Exception as e:
            logger.error(f"Error fetching thread {thread_id}: {e}")
            raise ValueError(f"Error accessing thread: {e}")

    @staticmethod
    def find_section_header(content: str) -> str:
        """Find a section header in the content"""
        for section in ThreadParser.KNOWN_SECTIONS:
            # Check for variations of the header format
            patterns = [
                f"{section}:?\\s*$",  # Plain text with optional colon
                f"#\\s*{section}:?\\s*$",  # Markdown heading
                f"\\*\\*{section}\\*\\*:?\\s*$",  # Bold text
                f"^.*?{section}:?\\s*$"  # More flexible match for Discord's rendering
            ]
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    return section
        return ""

    @staticmethod
    async def parse_thread(bot: commands.Bot, thread_input: str) -> Dict[str, Any]:
        """Parse a Discord thread to extract messages"""
        try:
            thread_id = ThreadParser.extract_thread_id(thread_input)
            thread = await ThreadParser.fetch_thread(bot, thread_id)
            
            sections = {}
            total_length = 0
            
            content_buffer = []
            thread_owner = None
            
            async for msg in thread.history(oldest_first=True):
                content = msg.content.strip()
                
                if not content:
                    continue
                    
                if not thread_owner:
                    thread_owner = msg.author
                
                #Break at voting options
                #NOTE: We default to Adopt / Reassess / Abstain, there is no need to include it.
                #However, in the future we may wish to use dynamic voting options and styles of votes.
                if "voting options" in content.lower():
                    break
                
                if msg.author == thread_owner:
                    content_buffer.append(content)
                    total_length += len(content)
                    
                    if total_length > 10000:
                        raise ValueError("Proposal content exceeds Snapshot's 10,000 character limit")
            
            full_content = '\n'.join(content_buffer)
            
            section_order = [
                "authors",
                "abstract",
                "definitions",
                "background",
                "Details",
                "implementation protocol"
            ]
            
            sections_found = {}
            for section in section_order:
                pos = full_content.lower().find(section)
                if pos != -1:
                    sections_found[pos] = section
            
            positions = sorted(sections_found.keys())
            
            for i, pos in enumerate(positions):
                section = sections_found[pos]
                next_pos = positions[i + 1] if i + 1 < len(positions) else len(full_content)
                content = full_content[pos:next_pos].strip()
                
                header_end = content.lower().find('\n')
                if header_end != -1:
                    content = content[header_end:].strip()
                    content = content.rstrip('*').rstrip('#').strip()
                
                sections[section.title()] = content
            
            title = thread.name
            
            draft_type = "budget"
            if thread.applied_tags:
                tag_name = thread.applied_tags[0].name.lower()
                if "governance" in tag_name or "improvement" in tag_name:
                    draft_type = "governance"
            
            return {
                "title": title,
                "type": draft_type,
                "sections": sections
            }
            
        except Exception as e:
            logger.error(f"Error parsing thread: {e}")
            return None