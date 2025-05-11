import discord
import json

from embed import embed_res

with open("commands_settings/embed_settings.json", "r", encoding="utf8") as f:
    EMBED_SETTINGS = json.load(f)

async def button_handler(bot, interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component and getattr(interaction.data, "component_type", None) != 2:
        return

    i_id = interaction.data["custom_id"].split("-")

    match(i_id[0]):
        case "role":
            rola = interaction.guild.get_role(int(i_id[1]))
            if rola in interaction.user.roles:
                await interaction.user.remove_roles(rola)
                return await embed_res(interaction, f"Usunięto rolę {rola.mention}")
            else:
                await interaction.user.add_roles(rola)
                return await embed_res(interaction, f"Dodano rolę {rola.mention}")

        case "embed":
            nazwa = i_id[1]
            if nazwa not in EMBED_SETTINGS.keys():
                return await embed_res(interaction, f"Nie znaleziono embedu `` {nazwa} ``", 0)
            embed_data = EMBED_SETTINGS[nazwa]["buttons"][int(i_id[2])]["embed"]
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
                            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        case _:
            return await embed_res(interaction, "Nie zdefiniowano odpowiedzi!", 0)
