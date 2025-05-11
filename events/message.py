import discord
import logging
import traceback
import time
import re
import settings

from reaction_utils import add_seen_reaction
from discord.ext import commands

async def message_handler(bot: commands.Bot, message: discord.Message):
    if message.author == bot.user:
        return
    if getattr(message, 'position', None) is None:
        try:
            await thread_handler(message)
            await add_seen_reaction(message)
        except Exception:
            logging.error(traceback.format_exc())
    elif get_thread_name(message.content) == '[cd]':
        try:
            await add_seen_reaction(message)
        except Exception:
            logging.error(traceback.format_exc())
    time.sleep(0.5)
    await doodle_handler(bot, message)
    await poll_handler(message)
    await event_handler(bot, message)
    
async def doodle_handler(bot, message: discord.Message):
    for doodle_link in settings.doodle_links:
        if doodle_link in message.content:
            channel = bot.get_channel(settings.doodle_channel_id)
            if channel is not None:
                new_message = await channel.send(message.jump_url + '\n>>> ' + message.content)
                await new_message.add_reaction(settings.doodle_seen_reaction)

async def poll_handler(message: discord.Message):
    options = re.findall(r'> - .+', message.content)
    for option in options:
        emoji = get_option_emoji(option)
        try:
            await message.add_reaction(emoji)
        except Exception as e:
            logging.error(f"Failed to add poll reaction: {e}")

async def event_handler(bot: commands.Bot, message: discord.Message):
    if message.channel.category_id == settings.events_archive:
        channel = message.channel if message.channel.type == discord.ChannelType.text else message.channel.parent
        
        channel_children = [{"name": c.name, "poss": c.position} for c in bot.get_channel(settings.events_category).channels]
        channel_children.append({"name": channel.name, "poss": -1})
        channel_children.sort(key=lambda x: x["name"])
        new_channel_pos = next((i for i, c in enumerate(channel_children) if c["name"] == channel.name), -1)
        
        await channel.move(category=discord.Object(id=settings.events_category), offset=new_channel_pos, beginning=True)
        print(f"Moved channel {channel.name} from inactive to active events category")

def get_option_emoji(option_string: str) -> str:
    emoji = option_string[4:].split()[0]
    if emoji[0] == '<' and emoji[-1] == '>':
        emoji = emoji[1:-1]
    return emoji

async def thread_handler(message: discord.Message):
    thread_name = get_thread_name(message.content)
    if thread_name is not None:
        thread = await message.create_thread(name = thread_name)
        await thread.send(f'<@&{settings.notify_role_id}>\nreactions:')
        
def get_thread_name(message_content: str) -> str | None:
    title = re.match(r'^[#*_>\s-]*\[(.*?)\]', message_content)
    return f'[{title.group(1)}]' if title else None
