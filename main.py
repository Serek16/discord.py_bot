from discord.ext import commands
import discord
import os


TOKEN = os.environ['BOT_TOKEN']
intents = discord.Intents.all()
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
