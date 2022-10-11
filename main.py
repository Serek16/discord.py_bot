from discord.ext import commands
import discord
import asyncio
import os

from utils.bot_utils import get_global, load_vars
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)

load_vars()

@bot.event
async def on_ready():
    print(f'\'{bot.user.name}\' is ready!')

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        bot.remove_command('help')
        await bot.start(get_global("bot_token"))

asyncio.run(main())