import discord
import json
import typing
import settings
from emoji import is_emoji
from discord import app_commands
from discord.ext import commands
from embed import embed_res

CONFIG_FILE = "commands_settings/role_settings.json"

class Role(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        try:
            with open(CONFIG_FILE, "r", encoding="utf8") as f:
                self.ROLE_SETTINGS = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {CONFIG_FILE}: {e}. Using empty settings.")
            self.ROLE_SETTINGS = {}

    def save_seen_settings(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.ROLE_SETTINGS, f, indent=4)

    group = app_commands.Group(
        name="role",
        description="Komenda do zarządzania grupami ról.",
        guild_ids=[settings.main_guild_id]
    )

    @group.command(name="lista", description="Wyświetla dostępne grupy ról.")
    @app_commands.describe(help="Wyświetl pomoc dla tej komendy")
    async def lista(self, interaction: discord.Interaction, help: bool = False) -> None:
        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /role lista",
                description="Wyświetla wszystkie dostępne grupy ról wraz z przypisanymi do nich rolami.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Pokazuje przegląd wszystkich utworzonych grup ról, wraz z emotkami i rolami przypisanymi do każdej grupy.",
                inline=False
            )
            embed.add_field(
                name="📝 Przykład użycia:",
                value="`/role lista help:True` - Ta pomoc\n`/role lista` - Pokaż wszystkie grupy ról",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="• Puste grupy będą oznaczone jako 'brak ról w grupie'\n• Każda grupa pokazuje emotkę i przypisaną rolę\n• Użyj `/role wyświetl` aby wysłać interaktywny panel ról",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        grupy = self.ROLE_SETTINGS.keys()
        embed = discord.Embed(title="Lista grup ról",
                              color=discord.Color.purple())

        [embed.add_field(name=f"Grupa: {x}", inline=False, value=(" | ".join(["{} <@&{}>".format(str(y["emotka"]), str(y["id"]))
                                for y in self.ROLE_SETTINGS[x]]) if len(self.ROLE_SETTINGS[x]) > 0 else "*brak ról w grupie*")) for x in grupy]

        return await interaction.response.send_message(embed=embed, ephemeral=True)

    @group.command(name="utwórz", description="Tworzy nową grupę ról.")
    @app_commands.describe(
        help="Wyświetl pomoc dla tej komendy",
        nazwa="Nazwa grupy."
    )
    async def utworz(self, interaction: discord.Interaction, help: bool = False, nazwa: str = None) -> None:
        if help and nazwa is not None:
            embed = discord.Embed(
                title="❌ Błąd parametrów",
                description="Parametr `help` nie może być używany razem z innymi parametrami.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /role utwórz",
                description="Tworzy nową pustą grupę ról.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Tworzy nową grupę ról, do której później można dodawać role za pomocą komendy `/role dodaj`.",
                inline=False
            )
            embed.add_field(
                name="📝 Przykłady użycia:",
                value="• `/role utwórz help:True` - Ta pomoc\n• `/role utwórz nazwa:gaming` - Utwórz grupę o nazwie 'gaming'",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="• Nazwa grupy musi być unikalna\n• Po utworzeniu grupy użyj `/role dodaj` aby dodać role",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if nazwa is None:
            return await embed_res(interaction, "Musisz podać nazwę grupy!", 0)

        if nazwa in self.ROLE_SETTINGS.keys():
            return await embed_res(interaction, "Grupa o podanej nazwie już istnieje!", 0)

        self.ROLE_SETTINGS[nazwa] = []
        self.save_seen_settings()
        return await embed_res(interaction, f"Poprawnie utworzono grupę ról o nazwie: `` {nazwa} ``!", 1)

    async def grupa_autocompletion(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=x, value=x) for x in self.ROLE_SETTINGS.keys() if current.lower() in x.lower()][:25]

    @group.command(name="dodaj", description="Dodaje rolę do wybrenej grupy.")
    @app_commands.describe(
        help="Wyświetl pomoc dla tej komendy",
        grupa="Grupa, do której mam dodać rolę.",
        rola="Rola, którą mam dodać do grupy.",
        emotka="Emotka przypisana do roli.",
        opis="Opis roli."
    )
    @app_commands.autocomplete(grupa=grupa_autocompletion)
    async def dodaj(self, interaction: discord.Interaction, help: bool = False, grupa: str = None, rola: discord.Role = None, emotka: str = None, opis: typing.Optional[str] = "") -> None:
        if help and (grupa is not None or rola is not None or emotka is not None or opis != ""):
            embed = discord.Embed(
                title="❌ Błąd parametrów",
                description="Parametr `help` nie może być używany razem z innymi parametrami.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /role dodaj",
                description="Dodaje rolę do wybranej grupy ról.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Dodaje rolę do istniejącej grupy ról z przypisaną emotką i opcjonalnym opisem.",
                inline=False
            )
            embed.add_field(
                name="📝 Przykłady użycia:",
                value="• `/role dodaj help:True` - Ta pomoc\n• `/role dodaj grupa:gaming rola:@Gamer emotka:🎮` - Dodaj rolę z emotką\n• `/role dodaj grupa:gaming rola:@Pro emotka:⭐ opis:Dla profesjonalistów` - Z opisem",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="• Grupa musi już istnieć (użyj `/role utwórz`)\n• Emotka musi być prawidłowa\n• Jedna emotka = jedna rola w grupie\n• Opis jest opcjonalny",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not all([grupa, rola, emotka]):
            return await embed_res(interaction, "Musisz podać wszystkie wymagane parametry!", 0)

        if not grupa in self.ROLE_SETTINGS.keys():
            return await embed_res(interaction, "Grupa o podanej nazwie nie istnieje!", 0)

        if not is_emoji(emotka):
            return await embed_res(interaction, "Podana emotka nie jest poprawna!", 0)

        if emotka in [x["emotka"] for x in self.ROLE_SETTINGS[grupa]]:
            return await embed_res(interaction, "Podana emotka jest już przypisana do innej roli w podanej grupie!", 0)

        if rola.id in [x["id"] for x in self.ROLE_SETTINGS[grupa]]:
            return await embed_res(interaction, "Podana rola jest już w podanej grupie!", 0)

        self.ROLE_SETTINGS[grupa].append({"emotka": emotka, "id": rola.id, "opis": opis})
        self.save_seen_settings()
        return await embed_res(interaction, f"Poprawnie dodano rolę {rola.mention} do grupy `` {grupa} ``!", 1)

    @group.command(name="usuń", description="Usuwa rolę z wybrenej grupy.")
    @app_commands.describe(
        help="Wyświetl pomoc dla tej komendy",
        grupa="Grupa, z której mam usunąć rolę.",
        emotka="Emotka przypisana do roli."
    )
    @app_commands.autocomplete(grupa=grupa_autocompletion)
    async def usun(self, interaction: discord.Interaction, help: bool = False, grupa: str = None, emotka: str = None) -> None:
        if help and (grupa is not None or emotka is not None):
            embed = discord.Embed(
                title="❌ Błąd parametrów",
                description="Parametr `help` nie może być używany razem z innymi parametrami.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /role usuń",
                description="Usuwa rolę z wybranej grupy ról.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Usuwa rolę z grupy na podstawie przypisanej do niej emotki.",
                inline=False
            )
            embed.add_field(
                name="📝 Przykłady użycia:",
                value="• `/role usuń help:True` - Ta pomoc\n• `/role usuń grupa:gaming emotka:🎮` - Usuń rolę z emotką 🎮",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="• Musisz podać dokładnie tę samą emotkę co przy dodawaniu\n• Po usunięciu roli z grupy, przestanie być dostępna w panelu ról",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not all([grupa, emotka]):
            return await embed_res(interaction, "Musisz podać wszystkie wymagane parametry!", 0)

        if not grupa in self.ROLE_SETTINGS.keys():
            return await embed_res(interaction, "Grupa o podanej nazwie nie istnieje!", 0)

        if not is_emoji(emotka):
            return await embed_res(interaction, "Podana emotka nie jest poprawna!", 0)

        if not emotka in [x["emotka"] for x in self.ROLE_SETTINGS[grupa]]:
            return await embed_res(interaction, "Podana emotka nie istnieje w podanej grupie!", 0)

        self.ROLE_SETTINGS[grupa] = [
            i for i in self.ROLE_SETTINGS[grupa] if i["emotka"] != emotka]

        self.save_seen_settings()
        return await embed_res(interaction, f"Poprawnie usunięto rolę `` {emotka} `` z grupy `` {grupa} ``!", 1)

    @group.command(name="wyświetl", description="Wysyła embed z wyborem ról.")
    @app_commands.describe(
        help="Wyświetl pomoc dla tej komendy",
        grupa="Grupa, którą mam wyświetlić."
    )
    @app_commands.autocomplete(grupa=grupa_autocompletion)
    async def wyswietl(self, interaction: discord.Interaction, help: bool = False, grupa: str = None) -> None:
        if help and grupa is not None:
            embed = discord.Embed(
                title="❌ Błąd parametrów",
                description="Parametr `help` nie może być używany razem z innymi parametrami.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /role wyświetl",
                description="Wysyła interaktywny panel wyboru ról z grupy.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Tworzy embed z przyciskami, które pozwalają użytkownikom dodawać/usuwać role przez kliknięcie odpowiedniej emotki.",
                inline=False
            )
            embed.add_field(
                name="📝 Przykłady użycia:",
                value="• `/role wyświetl help:True` - Ta pomoc\n• `/role wyświetl grupa:gaming` - Wyślij panel ról z grupy 'gaming'",
                inline=False
            )
            embed.add_field(
                name="💡 Wskazówki:",
                value="• Panel działa permanentnie - użytkownicy mogą klikać przyciski w dowolnym momencie\n• Kliknięcie przycisku dodaje rolę jeśli jej nie ma, lub usuwa jeśli już ją posiada",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if grupa is None:
            return await embed_res(interaction, "Musisz podać nazwę grupy!", 0)

        if not grupa in self.ROLE_SETTINGS.keys():
            return await embed_res(interaction, "Grupa o podanej nazwie nie istnieje!", 0)

        view = discord.ui.View(timeout=None)
        [view.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, emoji=x["emotka"], custom_id=f"role-{x['id']}")) for x in self.ROLE_SETTINGS[grupa]]

        desc = [f"{x['emotka']} - <@&{x['id']}>{f'`` {x["opis"]} ``' if 'opis' in x and x['opis'] != '' else ''}" for x in self.ROLE_SETTINGS[grupa]]

        embed = discord.Embed(title=f"Wybierz rolę z grupy: {grupa}", description="\n".join(
            desc), color=discord.Color.purple())

        embed.set_footer(
            text="Kliknij przycisk z odpowiednią emotką, aby nadać lub odebrać sobie rolę.")

        await interaction.channel.send(embed=embed, view=view)
        return await embed_res(interaction, f"Poprawnie wysłano wiadomość z rolami z grupy `` {grupa} ``!", 1)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Role(bot))
