from discord.ext import commands
import discord
import asyncio
import os
import sys
import argparse
from src.utils.config_val_io import GlobalValues

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--allow', nargs='+', help='list of extensions that will be loaded')
parser.add_argument('-i', '--ignore', nargs='+', help='list of extensions that will be ignored while loading')

args = parser.parse_args()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)


@bot.event
async def on_ready():
    print(f'\'{bot.user.name}\' is ready!')


async def load_extensions():

    if args.allow is not None and args.ignore is not None:
        print("Use either --allow or --ignore. Not both.")
        sys.exit(1)

    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):

            # Ignore this extensions if it is NOT in allowed list
            if args.allow is not None and filename[:-3] not in args.allow:
                continue

            # Ignore this extensions if it IS in ignored list
            if args.ignore is not None and filename[:-3] in args.ignore:
                continue

            print(f'Loading {filename}')
            await bot.load_extension(f".{filename[:-3]}", package='src.cogs')


async def main():
    async with bot:
        await load_extensions()
        bot.remove_command('help')  # Remove ";help" command
        await bot.start(GlobalValues.get("bot_token"))


asyncio.run(main())
from discord.ext import commands
import discord
import asyncio
import os
import sys
import argparse
from src.utils.config_val_io import GlobalValues

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--allow', nargs='+', help='list of extensions that will be loaded')
parser.add_argument('-i', '--ignore', nargs='+', help='list of extensions that will be ignored while loading')

args = parser.parse_args()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=';', intents=intents)


@bot.event
async def on_ready():
    print(f'\'{bot.user.name}\' is ready!')


async def load_extensions():

    if args.allow is not None and args.ignore is not None:
        print("Use either --allow or --ignore. Not both.")
        sys.exit(1)

    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):

            # Ignore this extensions if it NOT is in allowed list
            if args.allow is not None and filename[:-3] not in args.allow:
                continue

            # Ignore this extensions if it IS in ignored list
            if args.ignore is not None and filename[:-3] in args.ignore:
                continue

            print(f'Loading {filename}')
            await bot.load_extension(f".{filename[:-3]}", package='src.cogs')


async def main():
    async with bot:
        await load_extensions()
        bot.remove_command('help')  # Remove ";help" command
        await bot.start(GlobalValues.get("bot_token"))


asyncio.run(main())
