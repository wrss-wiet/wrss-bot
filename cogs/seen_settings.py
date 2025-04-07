import discord
from discord import app_commands
from discord.ext import commands
import json

CONFIG_FILE = "seen_settings.json"

try:
    with open(CONFIG_FILE, "r") as f:
        SEEN_SETTINGS = json.load(f)
except FileNotFoundError:
    SEEN_SETTINGS = {}

def save_seen_settings():
    with open(CONFIG_FILE, "w") as f:
        json.dump(SEEN_SETTINGS, f, indent=4)

class SeenSettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="seensettings", description="Konfiguracja ustawień reakcji seen dla kanałów.")
    @app_commands.describe(
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
    async def seensettings(self, interaction: discord.Interaction, channel: discord.TextChannel = None, mode: str = None, scope: str = "all"):
        if channel is not None and mode is not None:
            SEEN_SETTINGS[str(channel.id)] = mode
            save_seen_settings()
            embed = discord.Embed(
                title="Aktualizacja ustawień",
                description=f"Zaktualizowano ustawienie dla kanału {channel.mention} na `{mode}`.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if scope == "current":
                ch = interaction.channel
                setting = SEEN_SETTINGS.get(str(ch.id), "Always")
                embed = discord.Embed(
                    title=f"Ustawienie dla bieżącego kanału: {ch.name}",
                    description=f"**{ch.name}** (ID: {ch.id}): `{setting}`",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                guild = interaction.guild
                embed = discord.Embed(title="Obecne ustawienia seen dla kanałów", color=discord.Color.blue())
                description = ""
                for ch in guild.text_channels:
                    setting = SEEN_SETTINGS.get(str(ch.id), "Always")
                    description += f"**{ch.name}** (ID: {ch.id}): `{setting}`\n"
                embed.description = description
                await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SeenSettingsCog(bot))
