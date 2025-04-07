import discord
import traceback
import logging
import re
import time
import settings

from discord.ext import commands
from reaction_utils import add_seen_reaction

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def new_message_handler(message: discord.Message):
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
    await doodle_handler(message)
    await poll_handler(message)

async def doodle_handler(message: discord.Message):
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

async def reaction_change_handler(payload):
    if payload.user_id == bot.user.id:
        return
    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return
    message = await channel.fetch_message(payload.message_id)
    if getattr(message, 'position', None) is None:
        await update_reaction_msg(message)

def get_thread_name(message_content: str) -> str:
    title = re.search(r'\[[^\]]*\]', message_content)
    return title.group(0) if title is not None else None

def reactions_to_str(reactions) -> str:
    message = "reactions:\n"
    for reaction in reactions:
        message += f"{reaction.emoji}:{reaction.count} "
    return message

async def get_reaction_msg(message: discord.Message):
    thread = discord.utils.get(message.channel.threads, id = message.id)
    if thread is None:
        return None
    messages = [message async for message in thread.history(limit=2, oldest_first=True)]
    if len(messages) < 2 or messages[1].author != bot.user:
        return None
    return messages[1]

async def update_reaction_msg(message: discord.Message):
    reactions = message.reactions
    reaction_msg = await get_reaction_msg(message)
    if reaction_msg is not None:
        reaction_msg_content = reactions_to_str(reactions)
        await reaction_msg.edit(content=(f'<@&{settings.notify_role_id}>\n' + reaction_msg_content))

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        await bot.tree.sync()
        print("Application commands synchronized.")

        commands_list = [command.name for command in bot.tree.get_commands()]
        print(f"Registered commands: {commands_list}")

    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    await new_message_handler(message)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    await reaction_change_handler(payload)

@bot.event
async def on_raw_reaction_remove(payload):
    await reaction_change_handler(payload)

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.seen_settings")
    await bot.load_extension("cogs.zamowieniegrafik")

bot.run(settings.client_token)
