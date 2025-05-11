import discord
import settings

from events.ready import ready
from events.buttons import button_handler
from events.message import message_handler
from events.reaction import reaction_change_handler
from events.voice import voice_handler

from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await ready(bot)
    
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

async def setup_hook():
    bot.tree.clear_commands(guild=None)
    bot.tree.clear_commands(guild=discord.Object(id=settings.main_guild_id))

    await bot.load_extension("cogs.seen_settings")
    await bot.load_extension("cogs.zamowieniegrafik")
    await bot.load_extension("cogs.role")
    await bot.load_extension("cogs.embedy")
    await bot.load_extension("cogs.eventsarch_settings")

    try:
        await bot.tree.sync(guild=discord.Object(id=settings.main_guild_id))
        print("Application commands synchronized.")

        commands_list = [command.name for command in bot.tree.get_commands(guild=discord.Object(id=settings.main_guild_id))]
        print(f"Registered commands in guild: {settings.main_guild_id}: {commands_list}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    await voice_handler(bot, member, before, after)

bot.setup_hook = setup_hook
bot.run(settings.client_token)
