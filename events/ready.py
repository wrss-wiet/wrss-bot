import discord
import logging
import settings

async def ready_handler(bot):
    print(f'We have logged in as {bot.user}')
    try:
        bot.tree.copy_global_to(guild=discord.Object(id=settings.main_guild_id))
        await bot.tree.sync(guild=discord.Object(id=settings.main_guild_id))
        print("Application commands synchronized.")

        commands_list = [command.name for command in bot.tree.get_commands()]
        print(f"Registered commands: {commands_list}")

    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")