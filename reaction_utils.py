import discord
import settings
from discord import ChannelType
import re

from cogs.seen_settings import SEEN_SETTINGS

def get_thread_name(content: str) -> str:
    title = re.search(r'\[[^\]]*\]', content)
    return title.group(0) if title is not None else None

async def add_seen_reaction(message: discord.Message):
    mode = SEEN_SETTINGS.get(str(message.channel.id), "Always")
    if mode == "Always":
        if message.channel.type != ChannelType.public_thread:
            try:
                await message.add_reaction(settings.seen_emoji_long_id)
            except Exception as e:
                print(f"Error adding seen reaction in Always mode: {e}")
    elif mode == "ThreadsOnly":
        if get_thread_name(message.content):
            try:
                await message.add_reaction(settings.seen_emoji_long_id)
            except Exception as e:
                print(f"Error adding seen reaction in ThreadsOnly mode: {e}")
    elif mode == "Off":
        pass
