import discord
import settings

async def reaction_change_handler(bot, payload):
    if payload.user_id == bot.user.id:
        return
    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return
    message = await channel.fetch_message(payload.message_id)
    if getattr(message, 'position', None) is None:
        await update_reaction_msg(bot, message)

async def update_reaction_msg(bot, message: discord.Message):
    reactions = message.reactions
    reaction_msg = await get_reaction_msg(bot, message)
    if reaction_msg is not None:
        reaction_msg_content = reactions_to_str(reactions)
        await reaction_msg.edit(content=(f'<@&{settings.notify_role_id}>\n' + reaction_msg_content))

def reactions_to_str(reactions) -> str:
    message = "reactions:\n"
    for reaction in reactions:
        message += f"{reaction.emoji} - ` {reaction.count+8} `\n"
    return message

async def get_reaction_msg(bot, message: discord.Message):
    thread = discord.utils.get(message.channel.threads, id = message.id)
    if thread is None:
        return None
    messages = [message async for message in thread.history(limit=2, oldest_first=True)]
    if len(messages) < 2 or messages[1].author != bot.user:
        return None
    return messages[1]