import json
import discord
import settings
from discord import app_commands
from discord.ext import commands

CONFIG_FILE = "commands_settings/seen_settings.json"

try:
    with open(CONFIG_FILE, "r") as f:
        SEEN_SETTINGS = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading {CONFIG_FILE}: {e}. Using empty settings.")
    SEEN_SETTINGS = {}

def save_seen_settings():
    with open(CONFIG_FILE, "w") as f:
        json.dump(SEEN_SETTINGS, f, indent=4)

class SeenSettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="seensettings", description="Konfiguracja ustawień reakcji seen dla kanałów.")
    @app_commands.guilds(discord.Object(id=settings.main_guild_id))
    @app_commands.describe(
        help="Wyświetl pomoc dla tej komendy",
        channel="Wybierz kanał (opcjonalnie, tylko przy aktualizacji)",
        mode="Wybierz tryb działania reakcji seen (opcjonalnie, tylko przy aktualizacji)",
        scope="Zakres wyświetlonych ustawień: current - bieżący kanał, all - wszystkie (domyślnie)"
    )
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="Always", value="Always"),
            app_commands.Choice(name="Threads Only", value="ThreadsOnly"),
            app_commands.Choice(name="Off", value="Off")
        ],
        scope=[
            app_commands.Choice(name="Current", value="current"),
            app_commands.Choice(name="All", value="all")
        ]
    )
    async def seensettings(self, interaction: discord.Interaction, help: bool = False, channel: discord.TextChannel = None, mode: str = None, scope: str = "all"):

        if help and (channel is not None or mode is not None or scope != "all"):
            embed = discord.Embed(
                title="❌ Błąd parametrów",
                description="Parametr `help` nie może być używany razem z innymi parametrami.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /seensettings",
                description="Komenda do zarządzania systemem reakcji 'seen' (widziane) na wiadomościach.",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Pozwala konfigurować automatyczne dodawanie reakcji 'seen' do wiadomości w określonych kanałach. System posiada trzy tryby pracy.",
                inline=False
            )
            embed.add_field(
                name="⚙️ Tryby działania:",
                value="• **Always** - Zawsze dodaje reakcje\n• **ThreadsOnly** - Tylko w wątkach\n• **Off** - Wyłączone",
                inline=False
            )
            embed.add_field(
                name="📝 Przykłady użycia:",
                value="• `/seensettings help:True` - Ta pomoc\n• `/seensettings` - Pokaż wszystkie ustawienia\n• `/seensettings channel:#kanał mode:Always` - Ustaw tryb dla kanału\n• `/seensettings scope:current` - Pokaż ustawienia bieżącego kanału",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="• Każdy kanał może mieć swój własny tryb reakcji\n• Domyślnie wszystkie kanały mają tryb 'Always'\n• Zmiany są zapisywane automatycznie",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        if mode is not None:
            if channel is None:
                channel = interaction.channel

            SEEN_SETTINGS[str(channel.id)] = mode
            save_seen_settings()

            embed = discord.Embed(
                title="Aktualizacja ustawień",
                description=f"Zaktualizowano ustawienie dla kanału {channel.mention} na `{mode}`.",
                color=discord.Color.green()
            )
        else:
            if scope == "current":
                ch = interaction.channel
                try:
                    with open(CONFIG_FILE, "r") as f:
                        current_settings = json.load(f)
                    setting = current_settings.get(str(ch.id), "Always")
                except Exception:
                    setting = SEEN_SETTINGS.get(str(ch.id), "Always")

                embed = discord.Embed(
                    title=f"Ustawienie dla bieżącego kanału: {ch.name}",
                    description=f"**{ch.name}** (ID: {ch.id}): `{setting}`",
                    color=discord.Color.blue()
                )
            else:
                guild = interaction.guild
                embed = discord.Embed(title="Obecne ustawienia seen dla kanałów", color=discord.Color.blue())
                description = ""

                try:
                    with open(CONFIG_FILE, "r") as f:
                        current_settings = json.load(f)
                except Exception:
                    current_settings = SEEN_SETTINGS

                for ch in guild.text_channels:
                    setting = current_settings.get(str(ch.id), "Always")
                    description += f"**{ch.name}** (ID: {ch.id}): `{setting}`\n"

                embed.description = description

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SeenSettingsCog(bot))
