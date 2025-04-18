import discord
import settings

from events.buttons import button_handler
from events.message import message_handler
from events.reaction import reaction_change_handler
from events.ready import ready_handler
from events.voice import voice_handler

from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await ready_handler(bot)

@bot.event
async def on_message(message):
    await message_handler(bot, message)
    await bot.process_commands(message)

@bot.event
async def on_interaction(interaction):
    await button_handler(bot, interaction)
@bot.event
async def on_raw_reaction_add(payload):
    await reaction_change_handler(bot, payload)

@bot.event
async def on_raw_reaction_remove(payload):
    await reaction_change_handler(bot, payload)

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.seen_settings")
    await bot.load_extension("cogs.zamowieniegrafik")
    await bot.load_extension("cogs.role")
    await bot.load_extension("cogs.embedy")

@bot.event
async def on_voice_state_update(member, before, after):
    await voice_handler(bot, member, before, after)

bot.run(settings.client_token)
