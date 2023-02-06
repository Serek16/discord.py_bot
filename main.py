import argparse
import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands
from dpyConsole import Console

from src.utils.config_val_io import GlobalValues
from src.utils.logger import LOG_DIR

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--allow', nargs='+',
                    help='list of extensions that will be loaded')
parser.add_argument('-i', '--ignore', nargs='+',
                    help='list of extensions that will be ignored while loading')

args = parser.parse_args()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)

discord.utils.setup_logging(
    handler=logging.FileHandler(LOG_DIR + "exceptions.log")
)
discord.utils.setup_logging(
    handler=logging.StreamHandler(sys.stdout),
    level=logging.WARNING
)

console = Console(bot)


@console.command()
async def load(extension_name):
    try:
        await bot.load_extension(f".{extension_name}", package='src.cogs')
        print(f'Module \"{extension_name}\" has been loaded.')
    except Exception as e:
        print(e)


@console.command()
async def unload(extension_name):
    try:
        await bot.unload_extension(f".{extension_name}", package='src.cogs')
        print(f'Module \"{extension_name}\" has been unloaded.')
    except Exception as e:
        print(e)


@console.command()
async def reload(extension_name):
    try:
        await bot.reload_extension(f".{extension_name}", package='src.cogs')
        print(f'Module \"{extension_name}\" has been reloaded.')
    except Exception as e:
        print(e)


async def load_extensions():
    if args.allow is not None and args.ignore is not None:
        print("Use either --allow or --ignore. Not both.")
        sys.exit(1)

    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):

            # Ignore this extension if it is NOT in allowed list.
            if args.allow is not None and filename[:-3] not in args.allow:
                continue

            # Ignore this extension if it IS in ignored list.
            if args.ignore is not None and filename[:-3] in args.ignore:
                continue

            await bot.load_extension(f".{filename[:-3]}", package='src.cogs')
            print(f'Loaded {filename}')


@bot.event
async def on_ready():
    print(f'\'{bot.user.name}\' is ready!')


async def main():
    async with bot:
        await load_extensions()
        bot.remove_command('help')  # Remove ";help" command.
        await bot.start(GlobalValues.get("bot_token"))


console.start()
asyncio.run(main())
