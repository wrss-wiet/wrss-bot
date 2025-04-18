import discord
import json
import typing
import settings

from emoji import is_emoji
from discord import app_commands
from discord.ext import commands
from embed import embed_res

CONFIG_FILE = "role_settings.json"

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
        name="role", description="Komenda do zarządzania grupami ról.")

    @group.command(name="lista", description="Wyświetla dostępne grupy ról.")
    async def lista(self, interaction: discord.Interaction) -> None:

        grupy = self.ROLE_SETTINGS.keys()

        embed = discord.Embed(title="Lista grup ról",
                            color=discord.Color.purple())
        [embed.add_field(name=f"Grupa: {x}", inline=False, value=(" | ".join(["{} <@&{}>".format(str(y["emotka"]), str(y["id"]))
                        for y in self.ROLE_SETTINGS[x]]) if len(self.ROLE_SETTINGS[x]) > 0 else "*brak ról w grupie*")) for x in grupy]

        return await interaction.response.send_message(embed=embed, ephemeral=True)

    @group.command(name="utwórz", description="Tworzy nową grupę ról.")
    @app_commands.describe(nazwa="Nazwa grupy.")
    async def utworz(self, interaction: discord.Interaction, nazwa: str) -> None:

        if nazwa in self.ROLE_SETTINGS.keys():
            return await embed_res(interaction, "Grupa o podanej nazwie już istnieje!", 0)

        self.ROLE_SETTINGS[nazwa] = []
        self.save_seen_settings()

        return await embed_res(interaction, f"Poprawnie utworzono grupę ról o nazwie: `` {nazwa} ``!", 1)

    async def grupa_autocompletion(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=x, value=x) for x in self.ROLE_SETTINGS.keys() if current.lower() in x.lower()][:25]

    @group.command(name="dodaj", description="Dodaje rolę do wybrenej grupy.")
    @app_commands.describe(
        grupa="Grupa, do której mam dodać rolę.",
        rola="Rola, którą mam dodać do grupy.",
        emotka="Emotka przypisana do roli.",
        opis="Opis roli."
    )
    @app_commands.autocomplete(grupa=grupa_autocompletion)
    async def dodaj(self, interaction: discord.Interaction, grupa: str, rola: discord.Role, emotka: str, opis: typing.Optional[str] = "") -> None:
        if not grupa in self.ROLE_SETTINGS.keys():
            return await embed_res(interaction, "Grupa o podanej nazwie nie istnieje!", 0)
        if not is_emoji(emotka):
            return await embed_res(interaction, "Podana emotka nie jest poprawna!", 0)

        if emotka in [x["emotka"] for x in self.ROLE_SETTINGS[grupa]]:
            return await embed_res(interaction, "Podana emotka jest już przypisana do innej roli w podanej grupeie!", 0)
        if rola.id in [x["id"] for x in self.ROLE_SETTINGS[grupa]]:
            return await embed_res(interaction, "Podana rola jest już w podanej grupie!", 0)

        self.ROLE_SETTINGS[grupa].append({"emotka": emotka, "id": rola.id, "opis": opis})
        self.save_seen_settings()

        return await embed_res(interaction, f"Poprawnie dodano rolę {rola.mention} do grupy `` {grupa} ``!", 1)

    @group.command(name="usuń", description="Usuwa rolę z wybrenej grupy.")
    @app_commands.describe(
        grupa="Grupa, z której mam usunąć rolę.",
        emotka="Emotka przypisana do roli."
    )
    @app_commands.autocomplete(grupa=grupa_autocompletion)
    async def usun(self, interaction: discord.Interaction, grupa: str, emotka: str) -> None:
        if not grupa in self.ROLE_SETTINGS.keys():
            return await embed_res(interaction, "Grupa o podanej nazwie nie istnieje!", 0)
        if not is_emoji(emotka):
            return await embed_res(interaction, "Podana emotka nie jest poprawna!", 0)

        if not emotka in [x["emotka"] for x in self.ROLE_SETTINGS[grupa]]:
            return await embed_res(interaction, "Podana emotka nie istnieje w podanej grupie!", 0)

        self.ROLE_SETTINGS[grupa] = [
            i for i in self.ROLE_SETTINGS[grupa] if i["emotka"] != emotka]

        self.save_seen_settings()

        return await embed_res(interaction, f"Poprawnie usunięto rolę `` {emotka} `` do grupy `` {grupa} ``!", 1)

    @group.command(name="wyświetl", description="Wysyła embed z wyborem ról.")
    @app_commands.describe(grupa="Grupa, którą mam wyświetlić.")
    @app_commands.autocomplete(grupa=grupa_autocompletion)
    async def wyswietl(self, interaction: discord.Interaction, grupa: str) -> None:
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
