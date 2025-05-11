from datetime import datetime, timezone
import json
import settings
import discord

from discord.ext import tasks
from discord.ext import commands

async def ready(bot: commands.Bot):
    print(f"Logged in as {bot.user.name} in guild: {settings.main_guild_id}")
    ArchEventsLoop(bot).archive_events.start()

class ArchEventsLoop:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @tasks.loop(hours=6)
    async def archive_events(self):
        aktywne_kategoria = self.bot.get_channel(settings.events_category)
        
        for channel in aktywne_kategoria.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    last_message = await get_last_message(channel)

                    try:
                        with open("commands_settings/event_settings.json", "r") as f:
                            EVENT_SETTINGS = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError) as e:
                        EVENT_SETTINGS = {}
                        
                    INACTIVE_DAYS = EVENT_SETTINGS.get(str(channel.id), settings.def_archive)
                    print(INACTIVE_DAYS)
                    
                    if last_message:
                        delta = datetime.now(timezone.utc) - last_message.created_at

                        if delta.days >= INACTIVE_DAYS:
                            channel_children = [{"name": c.name, "poss": c.position} for c in self.bot.get_channel(settings.events_archive).channels]
                            channel_children.append({"name": channel.name, "poss": -1})
                            channel_children.sort(key=lambda x: x["name"])
                            new_channel_pos = next((i for i, c in enumerate(channel_children) if c["name"] == channel.name), -1)
                            
                            await channel.move(category=discord.Object(id=settings.events_archive), beginning=True, offset=new_channel_pos)
                            print(f"Moved channel {channel.name} to inactive (last message: {delta.days} days ago)")
                except Exception as e:
                    print(f"Error checking channel {channel.name}: {e}")

    @archive_events.before_loop
    async def before_archive_events(self):
        await self.bot.wait_until_ready()
        
        
async def get_last_message(channel: discord.TextChannel):
    try:
        temp = None
        async for message in channel.history(limit=1):
            temp = message
            
        for thread in channel.threads:
            async for message in thread.history(limit=1):
                if temp is None or message.created_at > temp.created_at:
                    temp = message
    except Exception as e:
        return None
    return temp
