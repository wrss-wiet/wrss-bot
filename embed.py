import discord


async def embed_res(interaction: discord.Interaction, description: str, state: int = 1) -> discord.Embed:
    e = discord.Embed(
        title="Wystąpił błąd!" if state == 0 else "Sukces!",
        description=f"❌ {description}" if state == 0 else f"✅ {description}",
        color=discord.Color.red() if state == 0 else discord.Color.green()
    )

    await interaction.response.send_message(embed=e, ephemeral=True)
