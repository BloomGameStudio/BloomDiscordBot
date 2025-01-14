from typing import Dict, Any
import discord
from discord.ext import commands
import re
from logger.logger import logger


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
        "Voting Options",
    ]

    @staticmethod
    def extract_thread_id(thread_input: str) -> int:
        """Extract thread ID from either a URL or direct ID"""
        try:
            if "discord.com" in thread_input:
                # Handle URLs with '/threads/' format
                if "/threads/" in thread_input:
                    thread_id = int(thread_input.split("/threads/")[1])
                else:
                    thread_id = int(thread_input.split("/")[-1])
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
                f"^.*?{section}:?\\s*$",  # More flexible match for Discord's rendering
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

            # Check for multiple proposal type tags
            governance_tag = False
            budget_tag = False

            if thread.applied_tags:
                for tag in thread.applied_tags:
                    tag_name = tag.name.lower()
                    if "governance" in tag_name or "improvement" in tag_name:
                        governance_tag = True
                    if "budget" in tag_name:
                        budget_tag = True

            if governance_tag and budget_tag:
                return (
                    None,
                    "A proposal cannot be both governance and budget type. Please apply only one tag.",
                )

            messages = []
            total_length = 0
            required_content = {
                "authors": False,
                "abstract": False,
                "background": False,
            }

            initial_author = None

            async for msg in thread.history(oldest_first=True):
                content = msg.content.strip()

                if not content:
                    continue

                # Set initial author from first message
                if initial_author is None:
                    initial_author = msg.author.id
                # If no voting options found and author changes, stop collecting messages
                elif msg.author.id != initial_author:
                    break

                content_lower = content.lower()

                # Check for required content within the message
                if "authors" in content_lower:
                    required_content["authors"] = True
                if "abstract" in content_lower:
                    required_content["abstract"] = True
                if "background" in content_lower:
                    required_content["background"] = True

                messages.append(content)
                total_length += len(content)

                if total_length > 10000:
                    return (
                        None,
                        "Your proposal content exceeds Snapshot's 10,000 character limit. Please shorten your proposal and try again.",
                    )

                # Return early if voting options are found
                if "voting options" in content_lower or "vote options" in content_lower:
                    return {
                        "title": thread.name,
                        "type": "budget"
                        if "budget" in thread.applied_tags[0].name.lower()
                        else "governance",
                        "sections": {
                            "content": "\n\n".join(messages),
                            "messages": messages,
                        },
                    }, None

            # Return the proposal data if no voting options were found
            return {
                "title": thread.name,
                "type": "budget"
                if "budget" in thread.applied_tags[0].name.lower()
                else "governance",
                "sections": {"content": "\n\n".join(messages), "messages": messages},
            }, None

        except Exception as e:
            logger.error(f"Error parsing thread: {e}")
            return None, str(e)
