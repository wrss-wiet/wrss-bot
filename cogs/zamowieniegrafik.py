import discord
from embed import embed_res
import settings

from discord.ext import commands
from discord import app_commands


class ZamowienieGrafika(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="zamowieniegrafik", description="Złóż zamówienie grafiki według szablonu")
    async def zamowieniegrafik(self, interaction: discord.Interaction):
        modal = ZamowienieGrafikaModal()
        await interaction.response.send_modal(modal)

def get_graphic_role_id(guild: discord.Guild) -> int:
    graphic_role_id = settings.graphic_role_id
    if graphic_role_id:
        try:
            return graphic_role_id
        except ValueError:
            print("GRAPHIC_ROLE_ID w env nie jest prawidłową liczbą.")
    for role in guild.roles:
        if role.name.lower() == "grafik":
            return role.id
    return 0

class ZamowienieGrafikaModal(discord.ui.Modal, title="Zamówienie grafiki"):
    nazwa = discord.ui.TextInput(
        label="Nazwa wydarzenia",
        placeholder="Wprowadź nazwę wydarzenia",
        required=True
    )
    co = discord.ui.TextInput(
        label="Co",
        placeholder="Opisz, co ma zostać wykonane",
        required=True
    )
    wymiary = discord.ui.TextInput(
        label="Wymiary",
        placeholder="Podaj wymiary grafiki (np. 1920x1080; A4; do dogadania)",
        required=True
    )
    deadline = discord.ui.TextInput(
        label="Deadline",
        placeholder="Podaj do kiedy",
        required=True
    )
    motyw_inne = discord.ui.TextInput(
        label="Motyw i Inne info",
        placeholder="Wprowadź motyw oraz dodatkowe informacje (oddzielone przecinkiem)",
        style=discord.TextStyle.paragraph,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Zamówienie grafiki", color=discord.Color.purple())
        embed.add_field(name="Nazwa wydarzenia", value=self.nazwa.value, inline=False)
        embed.add_field(name="Co", value=self.co.value, inline=False)
        embed.add_field(name="Wymiary", value=self.wymiary.value, inline=False)
        embed.add_field(name="Deadline", value=self.deadline.value, inline=False)
        embed.add_field(name="Motyw i Inne info", 
                        value=self.motyw_inne.value if self.motyw_inne.value else "Brak", 
                        inline=False)
        
        grafik_role_id = get_graphic_role_id(interaction.guild)
        role_mention = f"<@&{grafik_role_id}>" if grafik_role_id else "Brak roli 'Grafik'"
        
        # embed.add_field(name="Graficy", value=role_mention, inline=False)
        ordered_by = f"Zlecono przez: {interaction.user.display_name}"
        embed.set_footer(text=ordered_by)
        
        await embed_res(interaction, "Zamówienie grafiki zostało złożone!", 1)
        channel = interaction.channel
        order_message = await channel.send(role_mention, embed=embed)
        thread_name = f"Zamówienie: {self.nazwa.value}"
        try:
            await order_message.create_thread(name=thread_name)
        except Exception as e:
            print(f"Error creating thread: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ZamowienieGrafika(bot))
