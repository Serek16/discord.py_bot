from logger import get_logger
from discord.ext import commands
import sys
from config import config

sys.path.append('../')


logger = get_logger(__name__, __name__)


class Example(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        pass

    @commands.command()
    @commands.has_role(int(config("guild_ids")['staff']))
    async def hello(self, ctx):
        await ctx.send("Hello World!")


def setup(bot):
    bot.add_cog(Example(bot))
