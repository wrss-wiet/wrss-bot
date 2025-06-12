import json
import discord
import settings
from discord import app_commands
from discord.ext import commands
from embed import embed_res

CONFIG_FILE = "commands_settings/channel_settings.json"

try:
    with open(CONFIG_FILE, "r") as f:
        CHANNEL_SETTINGS = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading {CONFIG_FILE}: {e}. Using empty settings.")
    CHANNEL_SETTINGS = {}

def save_event_settings():
    with open(CONFIG_FILE, "w") as f:
        json.dump(CHANNEL_SETTINGS, f, indent=4)

class ChannelArchiveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="channelarchive", description="Konfiguracja automatycznego archiwizowania kanałów eventowych.")
    @app_commands.guilds(discord.Object(id=settings.main_guild_id))
    @app_commands.describe(
        help="Wyświetl pomoc dla tej komendy",
        channel="Wybierz kanał do konfiguracji (opcjonalnie)",
        dni="Liczba dni nieaktywności przed archiwizacją (0 = usuń ustawienie)"
    )
    async def channelarchive(self, interaction: discord.Interaction, help: bool = False, channel: discord.TextChannel = None, dni: app_commands.Range[int, 0, 30] = None):

        if help and (channel is not None or dni is not None):
            embed = discord.Embed(
                title="❌ Błąd parametrów",
                description="Parametr `help` nie może być używany razem z innymi parametrami.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /channelarchive",
                description="System automatycznego przenoszenia nieaktywnych kanałów eventowych do archiwum.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value=f"Automatycznie przenosi kanały z kategorii aktywnych eventów (<#{settings.events_category}>) do archiwum (<#{settings.events_archive}>) po określonym czasie nieaktywności.",
                inline=False
            )
            embed.add_field(
                name="⚙️ Jak to działa?",
                value=f"• Bot sprawdza kanały co 12 godzin\n• Jeśli ostatnia wiadomość jest starsza niż ustawiony czas - kanał idzie do archiwum\n• Gdy w zarchiwizowanym kanale pojawi się nowa wiadomość - wraca do aktywnych\n• Domyślny czas archiwizacji: **{settings.def_archive} dni**",
                inline=False
            )
            embed.add_field(
                name="📝 Przykłady użycia:",
                value="• `/channelarchive help:True` - Ta pomoc\n• `/channelarchive` - Pokaż wszystkie ustawienia\n• `/channelarchive channel:#event-kanał dni:7` - Ustaw 7 dni dla kanału\n• `/channelarchive channel:#event-kanał dni:0` - Usuń indywidualne ustawienie",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="• Każdy kanał może mieć swój własny czas archiwizacji\n• Kanały bez indywidualnych ustawień używają czasu domyślnego\n• Komenda działa tylko dla kanałów w określonych kategoriach.",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if dni is not None:
            if channel is None:
                channel = interaction.channel

            if not any(channel.category_id == x for x in [settings.events_category, settings.events_archive]):
                return await embed_res(interaction, "Nie można ustawić archiwizacji dla tego kanału.", 0)

            if dni == 0:
                if str(channel.id) in CHANNEL_SETTINGS:
                    del CHANNEL_SETTINGS[str(channel.id)]
                    save_event_settings()
                    return await embed_res(interaction, f"Usunięto ustawienie archiwizacji dla kanału {channel.mention}.", 1)
                else:
                    return await embed_res(interaction, "Nie znaleziono ustawienia archiwizacji dla tego kanału.", 0)

            CHANNEL_SETTINGS[str(channel.id)] = dni
            save_event_settings()
            return await embed_res(interaction, f"Zaktualizowano ustawienie dla kanału {channel.mention} na `{dni}` dni archiwizacji.", 1)
        else:
            description = ""
            if channel is None:
                for ch_id, dni in CHANNEL_SETTINGS.items():
                    description += f"<#{ch_id}> - `{dni}` dni archiwizacji\n"
                description += f"Reszta kanałów - ustawienia domyślne: `{settings.def_archive}` dni archiwizacji"
            else:
                if not any(channel.category_id == x for x in [settings.events_category, settings.events_archive]):
                    return await embed_res(interaction, "Ten kanał nie podlega archiwizacji.", 0)

                if not str(channel.id) in CHANNEL_SETTINGS:
                    dni = settings.def_archive
                else:
                    dni = CHANNEL_SETTINGS[str(channel.id)]

                description = f"<#{channel.id}> - `{dni}` dni archiwizacji\n"

            embed = discord.Embed(
                title="Ustawienia archiwizacji kanałów",
                description=description if description else f"Wszystkie kanały mają domyślne ustawienia archiwizacji ({settings.def_archive} dni).",
                color=discord.Color.green()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelArchiveCog(bot))
