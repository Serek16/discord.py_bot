import threading
from discord.ext import commands
import discord
import os
import asyncio

from logger import get_logger
from utils.bot_utils import get_global, load_vars

intents = discord.Intents.all()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=';', intents=intents)
logger = get_logger(__name__)

selfbot = None

def init_selfbot():
    import discum
    global selfbot
    selfbot = discum.Client(get_global('selfbot_token'), log=False)
    if selfbot is None:
        logger.error("Couldn't connect to selfbot")
    selfbot.gateway.run()


def getSelfBot():
    return selfbot

self_bot_thread = threading.Thread(target=init_selfbot)
self_bot_thread.start()
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