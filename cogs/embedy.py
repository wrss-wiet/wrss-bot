import discord
import json
import settings
from discord.ext import commands
from discord import app_commands
from embed import embed_res

CONFIG_FILE = "commands_settings/embed_settings.json"

class Embedy(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        try:
            with open(CONFIG_FILE, "r", encoding="utf8") as f:
                self.EMBED_SETTINGS = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {CONFIG_FILE}: {e}. Using empty settings.")
            self.EMBED_SETTINGS = {}

    def save_seen_settings(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.EMBED_SETTINGS, f, indent=4)

    grupa = discord.app_commands.Group(
        name="embed",
        description="Komendy do embedów",
        guild_ids=[settings.main_guild_id]
    )

    @grupa.command(name="lista", description="Lista zapisanych embedów.")
    @app_commands.describe(help="Wyświetl pomoc dla tej komendy")
    async def lista(self, interaction: discord.Interaction, help: bool = False):
        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /embed lista",
                description="Wyświetla wszystkie zapisane embedy w systemie.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Pokazuje nazwy wszystkich embedów zapisanych w bazie danych bota.",
                inline=False
            )
            embed.add_field(
                name="📝 Przykład użycia:",
                value="`/embed lista help:True` - Ta pomoc\n`/embed lista` - Pokaż wszystkie embedy",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="• Jeśli nie ma zapisanych embedów, wyświetli się informacja o ich braku\n• Nazwy embedów można użyć w komendzie `/embed wyślij`",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embedy = self.EMBED_SETTINGS.keys()
        embed = discord.Embed(title="Lista embedów", color=discord.Color.purple())
        embed.description = " | ".join([f"`` {x} ``" for x in embedy]) if embedy else "*brak zapisanych embedów*"
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    @grupa.command(name="zapisz", description="Zapisz embed.")
    @app_commands.describe(
        help="Wyświetl pomoc dla tej komendy",
        nazwa="Nazwa embedu"
    )
    async def zapisz(self, interaction: discord.Interaction, help: bool = False, nazwa: str = None):
        if help and nazwa is not None:
            embed = discord.Embed(
                title="❌ Błąd parametrów",
                description="Parametr `help` nie może być używany razem z innymi parametrami.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /embed zapisz",
                description="Zapisuje nowy embed w systemie.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Otwiera formularz do utworzenia nowego embedu i zapisuje go pod podaną nazwą.",
                inline=False
            )
            embed.add_field(
                name="📝 Przykłady użycia:",
                value="• `/embed zapisz help:True` - Ta pomoc\n• `/embed zapisz nazwa:regulamin` - Utwórz embed o nazwie 'regulamin'",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="• Nazwa embedu musi być unikalna\n• Formularz zawiera pola: tytuł, treść, URL, kolor i URL obrazu\n• Kolor podaj w formacie hex (np. 66ccff)",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if nazwa is None:
            return await embed_res(interaction, "Musisz podać nazwę embedu!", 0)

        modal = EmbedModal()
        modal.nazwa = nazwa
        modal.bot = self.bot
        await interaction.response.send_modal(modal)

    async def wyslij_autocomplete(self, interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=x, value=x) for x in self.EMBED_SETTINGS.keys() if current.lower() in x.lower()][:25]

    @grupa.command(name="wyślij", description="Wyślij embed.")
    @app_commands.describe(
        help="Wyświetl pomoc dla tej komendy",
        nazwa="Nazwa embedu"
    )
    @app_commands.autocomplete(nazwa=wyslij_autocomplete)
    async def wyslij(self, interaction: discord.Interaction, help: bool = False, nazwa: str = None):
        if help and nazwa is not None:
            embed = discord.Embed(
                title="❌ Błąd parametrów",
                description="Parametr `help` nie może być używany razem z innymi parametrami.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /embed wyślij",
                description="Wysyła wcześniej zapisany embed na kanał.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Pobiera zapisany embed z bazy danych i wysyła go na bieżący kanał. Jeśli embed zawiera przyciski, również je dodaje.",
                inline=False
            )
            embed.add_field(
                name="📝 Przykłady użycia:",
                value="• `/embed wyślij help:True` - Ta pomoc\n• `/embed wyślij nazwa:regulamin` - Wyślij embed o nazwie 'regulamin'",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="Użyj `/embed lista` aby zobaczyć dostępne embedy do wysłania.",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if nazwa is None:
            return await embed_res(interaction, "Musisz podać nazwę embedu!", 0)

        if not nazwa in self.EMBED_SETTINGS.keys() or nazwa == "default":
            return await embed_res(interaction, f"Nie znaleziono embedu `` {nazwa} ``", 0)

        embed_data = self.EMBED_SETTINGS.get(nazwa)
        embed = discord.Embed()

        for key, value in embed_data.items():
            if key in ["title", "description", "url", "color"]:
                if key == "color":
                    setattr(embed, key, int(value, 16))
                else:
                    setattr(embed, key, value)
            else:
                if key == "footer":
                    embed.set_footer(text=value.get("text", ""), icon_url=value.get("icon_url", ""))
                elif key == "image":
                    embed.set_image(url=value)
                elif key == "thumbnail":
                    embed.set_thumbnail(url=value)
                elif key == "author":
                    embed.set_author(name=value.get("name", ""), url=value.get("url", ""), icon_url=value.get("icon_url", ""))
                elif key == "fields":
                    for field in value:
                        embed.add_field(name=field["name"], value=field["value"], inline=field.get("inline", False))

        view = discord.ui.View(timeout=None)

        if "buttons" in embed_data.keys():
            for i in range(len(embed_data["buttons"])):
                btn_data = embed_data["buttons"][i]

                if "url" in btn_data:
                    button = discord.ui.Button(
                        label=btn_data.get("label", ""),
                        style=discord.ButtonStyle.link,
                        url=btn_data["url"]
                    )
                else:
                    button = discord.ui.Button(
                        label=btn_data.get("label", ""),
                        style=discord.ButtonStyle[btn_data.get("style", "primary").lower()],
                        custom_id=f"embed-{nazwa}-{i}"
                    )

                if "emoji" in btn_data:
                    button.emoji = btn_data["emoji"]

                view.add_item(button)

        await interaction.channel.send(embed=embed, view=view)
        return await embed_res(interaction, f"Wysłano embed `` {nazwa} ``", 1)

class EmbedModal(discord.ui.Modal, title="Embed"):
    _title = discord.ui.TextInput(label="Tytuł", required=True)
    _description = discord.ui.TextInput(label="Treść", required=True, style=discord.TextStyle.long)
    _url = discord.ui.TextInput(label="URL", required=False)
    _color = discord.ui.TextInput(label="Kolor (hex)", required=False, min_length=6, max_length=6, default="66ccff")
    _image_url = discord.ui.TextInput(label="URL obrazu", required=False)

    async def on_submit(self, interaction):
        embed_data = {}

        for x in ["_title", "_description", "_url", "_color", "_image_url"]:
            embed_data[x.replace("_", "")] = getattr(self, x).value if getattr(self, x).value else None

        if embed_data[x.replace("_", "")] is not None:
            embed_data[x.replace("_", "")] = self.__getattribute__(x).value

        self.bot.get_cog('Embedy').EMBED_SETTINGS[self.nazwa] = embed_data
        self.bot.get_cog('Embedy').save_seen_settings()

        return await embed_res(interaction, f"Zapisano embed `` {self.nazwa} ``", 1)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Embedy(bot))
