import discord
import settings

async def voice_handler(bot, member: discord.member, old_voice: discord.VoiceState, new_voice: discord.VoiceState):
    if new_voice.channel and getattr(new_voice.channel, "id", False) == settings.voice_creator:
        category = next(x for x in member.guild.categories if x.id == new_voice.channel.category_id)
        new_channel = await member.guild.create_voice_channel(f"Spotkanie {member}", category=category)
        
        await member.move_to(new_channel)
        
    if old_voice.channel and getattr(old_voice.channel, "category_id") == settings.vc_category and not getattr(old_voice.channel, "id") == settings.voice_creator:
        if len(old_voice.channel.members) == 0 or all([x if x.bot else False for x in old_voice.channel.members ]):
            try:
                await old_voice.channel.delete()
            except Exception:
                pass