from discord.ext import commands

from config import config

class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(int(config("guild_ids")['staff']))
    async def help(self, ctx):
        pass

def setup(bot):
    bot.add_cog(Help(bot))