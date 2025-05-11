import discord
import settings
import re
import json

from discord import ChannelType

def get_thread_name(content: str) -> str:
    title = re.search(r'\[[^\]]*\]', content)
    return title.group(0) if title is not None else None

async def add_seen_reaction(message: discord.Message):
    try:
        with open("commands_settings/seen_settings.json", "r") as f:
            current_settings = json.load(f)
    except Exception as e:
        print(f"Error loading commands_settings/seen_settings.json: {e}")
        current_settings = {}

    channel_id_str = str(message.channel.id)
    mode = current_settings.get(channel_id_str, "Always")
    print(f"Channel ID: {message.channel.id}, Channel name: {message.channel.name}, Mode: {mode}")

    if mode == "Always":
        if message.channel.type != ChannelType.public_thread:
            try:
                await message.add_reaction(settings.seen_emoji_long_id)
                print(f"Added 'seen' reaction (Always mode) to message in channel {message.channel.name}")
            except Exception as e:
                print(f"Error adding seen reaction in Always mode: {e}")
    elif mode == "ThreadsOnly":
        if get_thread_name(message.content):
            try:
                await message.add_reaction(settings.seen_emoji_long_id)
                print(f"Added 'seen' reaction (ThreadsOnly mode) to message in channel {message.channel.name}")
            except Exception as e:
                print(f"Error adding seen reaction in ThreadsOnly mode: {e}")
    elif mode == "Off":
        print(f"Skipping 'seen' reaction (Off mode) for channel {message.channel.name}")
