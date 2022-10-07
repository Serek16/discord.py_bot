from discord.ext import commands
import sys
import random

sys.path.append('../')


class Responses(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if message.content.startswith("Im not gay")\
            or message.content.startswith("I'm not gay")\
            or message.content.startswith("I am not gay")\
            or message.content.startswith("Im not a furry")\
            or message.content.startswith("I'm not a furry")\
            or message.content.startswith("I am not a furry")\
            or message.content.startswith("Im not furry")\
            or message.content.startswith("I'm not furry")\
            or message.content.startswith("I am not furry")\
            or message.content.startswith("Im not a femboy")\
            or message.content.startswith("I'm not a femboy")\
            or message.content.startswith("I am not a femboy")\
            or message.content.startswith("Im not femboy")\
            or message.content.startswith("I'm not femboy")\
            or message.content.startswith("I am not femboy"):

            randVal = random.random()
            if randVal >= 0.80:
                await message.channel.send("Yes, yes you are")
            elif randVal >= 0.60:
                await message.channel.send("Are you sure about that?")
            elif randVal >= 0.40:
                await message.channel.send("Don't lie")
            elif randVal >= 0.20:
                await message.channel.send("Everyone knows you are though")
            else:
                await message.channel.send("yes :clap: you :clap: are")


async def setup(bot):
    await bot.add_cog(Responses(bot))
