from discord.ext import commands
import discord
import os

from discord_bot_v2.config import config


TOKEN = config(section="bot_tokens")['bot']
intents = discord.Intents.all()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=';', intents=intents)


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')


@bot.event
async def on_ready():
    print(f'\'{bot.user.name}\' is ready!')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(TOKEN)
