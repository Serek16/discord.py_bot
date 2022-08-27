import threading
from discord.ext import commands
import discord
import os

from config import config
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
    selfbot = discum.Client(
        token=config(section="bot_tokens")['selfbot'], log=False)
    if selfbot is None:
        logger.error("Couldn't connect to selfbot")
    selfbot.gateway.run()


def getSelfBot():
    return selfbot


self_bot_thread = threading.Thread(target=init_selfbot)
self_bot_thread.start()


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')


@bot.event
async def on_ready():
    print(f'\'{bot.user.name}\' is ready!')

load_vars()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(get_global("BOT_TOKEN"))