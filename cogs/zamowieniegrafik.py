import discord
from discord.ext import commands
from discord import app_commands
import settings
from embed import embed_res

def get_graphic_role_id(guild: discord.Guild) -> int:
    try:
        return settings.graphic_role_id
    except Exception:
        for role in guild.roles:
            if role.name.lower() == "grafik":
                return role.id
        return 0

class ZamowienieGrafika(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="zamowieniegrafik",
        description="Złóż nowe lub edytuj istniejące zamówienie grafiki"
    )
    @app_commands.guilds(discord.Object(id=settings.main_guild_id))
    @app_commands.describe(
        help="Wyświetl pomoc dla tej komendy",
        edytuj="ID wiadomości z zamówieniem do edycji (opcjonalne)"
    )
    async def zamowieniegrafik(
        self,
        interaction: discord.Interaction,
        help: bool = False,
        edytuj: str = None
    ):

        if help and edytuj is not None:
            embed = discord.Embed(
                title="❌ Błąd parametrów",
                description="Parametr `help` nie może być używany razem z innymi parametrami.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if help:
            embed = discord.Embed(
                title="📖 Pomoc: /zamowieniegrafik",
                description="System zamawiania grafik z automatycznym powiadomieniem grafików.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎯 Co robi ta komenda?",
                value="Tworzy strukturalne zamówienie grafiki z wszystkimi niezbędnymi informacjami i automatycznie powiadamia zespół grafików.",
                inline=False
            )
            embed.add_field(
                name="📝 Przykłady użycia:",
                value="• `/zamowieniegrafik help:True` - Ta pomoc\n• `/zamowieniegrafik` - Nowe zamówienie\n• `/zamowieniegrafik edytuj:123456789` - Edytuj zamówienie o ID",
                inline=False
            )
            embed.add_field(
                name="💡 Funkcje:",
                value="• Automatyczne utworzenie wątku do dyskusji\n• Powiadomienie roli grafików\n• Możliwość edycji istniejących zamówień\n• Strukturalny formularz z wszystkimi szczegółami",
                inline=False
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        message_id = None
        if edytuj:
            try:
                message_id = int(edytuj)
            except ValueError:
                return await embed_res(interaction, "Podano nieprawidłowe ID wiadomości.", 0)

        if message_id:
            await self._start_edit_flow(interaction, message_id)
        else:
            await self._start_new_flow(interaction)

    async def _start_new_flow(self, interaction: discord.Interaction):
        modal = NewGrafikaModal()
        await interaction.response.send_modal(modal)

    async def _start_edit_flow(
        self,
        interaction: discord.Interaction,
        edytuj: int
    ):
        try:
            msg = await interaction.channel.fetch_message(edytuj)
        except discord.NotFound:
            return await embed_res(interaction, "Nie znaleziono wiadomości o podanym ID.", 0)

        if not msg.embeds or msg.embeds[0].title != "Zamówienie grafiki":
            return await embed_res(interaction, "To nie jest zamówienie grafiki.", 0)

        data = {f.name: f.value for f in msg.embeds[0].fields}
        modal = EditGrafikaModal(original_data=data, msg=msg)
        await interaction.response.send_modal(modal)

class NewGrafikaModal(discord.ui.Modal, title="Zamówienie grafiki"):
    nazwa = discord.ui.TextInput(label="Nazwa wydarzenia", required=True)
    co = discord.ui.TextInput(label="Co", required=True)
    wymiary = discord.ui.TextInput(label="Wymiary", required=True)
    deadline = discord.ui.TextInput(label="Deadline", required=True)
    motyw_inne = discord.ui.TextInput(
        label="Motyw i Inne info",
        style=discord.TextStyle.long,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Zamówienie grafiki", color=discord.Color.purple())
        embed.add_field(name="Nazwa wydarzenia", value=self.nazwa.value, inline=False)
        embed.add_field(name="Co", value=self.co.value, inline=False)
        embed.add_field(name="Wymiary", value=self.wymiary.value, inline=False)
        embed.add_field(name="Deadline", value=self.deadline.value, inline=False)
        embed.add_field(
            name="Motyw i Inne info",
            value=self.motyw_inne.value or "Brak",
            inline=False
        )

        grafik_role = get_graphic_role_id(interaction.guild)
        role_mention = f"<@&{grafik_role}>" if grafik_role else "Brak roli 'Grafik'"

        embed.set_footer(text=f"Zlecono przez: {interaction.user.display_name}")

        await embed_res(interaction, "Zamówienie grafiki zostało złożone!", 1)

        order_msg = await interaction.channel.send(role_mention, embed=embed)

        embed.set_footer(text=f"Zlecono przez: {interaction.user.display_name} \nID wiadomości: {order_msg.id}")

        await order_msg.edit(
            content=f"<@&{grafik_role}>",
            embed=embed
        )

        try:
            await order_msg.create_thread(name=f"Zamówienie: {self.nazwa.value}")
        except Exception:
            pass

class EditGrafikaModal(discord.ui.Modal, title="Edytuj zamówienie grafiki"):
    nazwa = discord.ui.TextInput(label="Nazwa wydarzenia", required=True)
    co = discord.ui.TextInput(label="Co", required=True)
    wymiary = discord.ui.TextInput(label="Wymiary", required=True)
    deadline = discord.ui.TextInput(label="Deadline", required=True)
    motyw = discord.ui.TextInput(
        label="Motyw i Inne info",
        style=discord.TextStyle.long,
        required=False
    )

    def __init__(self, original_data: dict, msg: discord.Message):
        super().__init__()
        self.nazwa.default = original_data.get("Nazwa wydarzenia", "")
        self.co.default = original_data.get("Co", "")
        self.wymiary.default = original_data.get("Wymiary", "")
        self.deadline.default = original_data.get("Deadline", "")
        self.motyw.default = original_data.get("Motyw i Inne info", "")
        self._msg = msg

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Zamówienie grafiki", color=discord.Color.purple())
        embed.add_field(name="Nazwa wydarzenia", value=self.nazwa.value, inline=False)
        embed.add_field(name="Co", value=self.co.value, inline=False)
        embed.add_field(name="Wymiary", value=self.wymiary.value, inline=False)
        embed.add_field(name="Deadline", value=self.deadline.value, inline=False)
        embed.add_field(
            name="Motyw i Inne info",
            value=self.motyw.value or "Brak",
            inline=False
        )

        embed.set_footer(text=f"Zlecono przez: {interaction.user.display_name} \nID wiadomości: {self._msg.id}")

        await self._msg.edit(embed=embed)
        await embed_res(interaction, "Zamówienie zaktualizowane!", 1)

async def setup(bot: commands.Bot):
    await bot.add_cog(ZamowienieGrafika(bot))
