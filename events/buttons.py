import discord
from embed import *


async def button_handler(bot, interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component and getattr(interaction.data, "component_type", None) != 2:
        return

    i_id = interaction.data["custom_id"]

    match(i_id.split("-")[0]):
        case "role":
            rola = interaction.guild.get_role(int(i_id.split("-")[1]))
            if rola in interaction.user.roles:
                await interaction.user.remove_roles(rola)
                return await embed_res(interaction, f"Usunięto rolę {rola.mention}")
            else:
                await interaction.user.add_roles(rola)
                return await embed_res(interaction, f"Dodano rolę {rola.mention}")

        case _:
            return await embed_res(interaction, "Nie zdefiniowano odpowiedzi!", 0)
