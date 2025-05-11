import json
import discord
import settings

from discord import app_commands
from discord.ext import commands

from embed import embed_res

CONFIG_FILE = "commands_settings/event_settings.json"

try:
    with open(CONFIG_FILE, "r") as f:
        EVENT_SETTINGS = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading {CONFIG_FILE}: {e}. Using empty settings.")
    EVENT_SETTINGS = {}

def save_event_settings():
    with open(CONFIG_FILE, "w") as f:
        json.dump(EVENT_SETTINGS, f, indent=4)

class EventSettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="eventsettings", description="Konfiguracja ustawień archiwizacji wydarzeń dla kanałów.")
    @app_commands.guilds(discord.Object(id=settings.main_guild_id))
    @app_commands.describe(
        channel="Wybierz kanał (opcjonalnie, tylko przy aktualizacji)",
        dni="Wybierz dni archiwizacji (opcjonalnie, tylko przy aktualizacji)"
    )
    async def eventsettings(self, interaction: discord.Interaction, channel: discord.TextChannel = None, dni: app_commands.Range[int, 0, 30] = None):
        if dni is not None:
            if channel is None:
                channel = interaction.channel
            if not any(channel.category_id == x for x in [settings.events_category, settings.events_archive]):
                return await embed_res(interaction, "Nie można ustawić archiwizacji dla tego kanału.", 0)
            
            if dni == 0:
                if str(channel.id) in EVENT_SETTINGS:
                    del EVENT_SETTINGS[str(channel.id)]
                    save_event_settings()
                    return await embed_res(interaction, f"Usunięto ustawienie archiwizacji dla kanału {channel.mention}.", 1)
                else:
                    return await embed_res(interaction, "Nie znaleziono ustawienia archiwizacji dla tego kanału.", 0)

            EVENT_SETTINGS[str(channel.id)] = dni
            save_event_settings()

            return await embed_res(interaction, f"Zaktualizowano ustawienie dla kanału {channel.mention} na `{dni}` dni archiwizacji.", 1)
        else:
            description = ""
            if channel is None:
                for ch_id, dni in EVENT_SETTINGS.items():
                    description += f"<#{ch_id}> - `{dni}` dni archiwizacji\n"
                description += f"Reszta kanałów - ustawienia domyślne: `{settings.def_archive}` dni archiwizacji"
            else:
                if not any(channel.category_id == x for x in [settings.events_category, settings.events_archive]):
                    return await embed_res(interaction, "Ten kanał nie podlega archiwizacji.", 0)
                if not str(channel.id) in EVENT_SETTINGS:
                    dni = settings.def_archive
                else:
                    dni = EVENT_SETTINGS[str(channel.id)]
                description = f"<#{channel.id}> - `{dni}` dni archiwizacji\n"
                
            embed = discord.Embed(
                title="Ustawienia archiwizacji wydarzeń",
                description=description if description else f"Wszystkie kanały mają domyślne ustawienia archiwizacji ({settings.def_archive} dni).",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
                
async def setup(bot: commands.Bot):
    await bot.add_cog(EventSettingsCog(bot))