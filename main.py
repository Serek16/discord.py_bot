from discord.ext import commands
import discord
import asyncio
import os
import sys

from src.utils.bot_utils import get_global, load_vars

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)

load_vars()


@bot.event
async def on_ready():
    print(f'\'{bot.user.name}\' is ready!')


async def load_extensions():
    modules = sys.argv[2:]

    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):
            if len(sys.argv) == 1 or (len(sys.argv) > 1
                                      and ((sys.argv[1] == 'allow' and filename[:-3] in modules)
                                           or (sys.argv[1] == 'block' and filename[:-3] not in modules))):
                await bot.load_extension(f".{filename[:-3]}", package='src.cogs')


async def main():
    async with bot:
        await load_extensions()
        bot.remove_command('help')
        await bot.start(get_global("bot_token"))


asyncio.run(main())
