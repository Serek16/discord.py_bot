from discord.ext import commands
import discord
import sys  

sys.path.append('../')
from logger import get_logger

logger = get_logger(__name__)


class Purge(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(910458855023083577)
    async def purge(self, ctx, arg1, arg2=None):
        '''Remove messages from the channel on which the command was used'''
        
        # if arg1 isn't None, use treat arg1 as the latest message 
        # and arg2 as the oldest message
        if arg2 != None:
            temp = arg1
            arg1 = arg2
            arg2 = temp
        
        # check if arg1/arg2 is an int
        try:
            arg1 = int(arg1)
        except ValueError:
            logger.warn("arg1 has to be a message id")
            await ctx.send("arg1 has to be a message id")
            return

        if arg2 != None:
            try:
                arg2 = int(arg2)
            except ValueError:
                logger.warn("arg2 has to a message id")
                await ctx.send("arg2 has to a message id")
                return

            try:
                await ctx.fetch_message(arg1)
            except discord.NotFound:
                logger.warn("Couldn't find the first argument message")
                await ctx.send("Couldn't find the first argument message")
                return

            if arg2 != None:
                try:
                    await ctx.fetch_message(arg2)
                except discord.NotFound:
                    logger.warn("Couldn't find the second argument message")
                    await ctx.send("Couldn't find the second argument message")
                    return


        # remove command message
        await ctx.message.delete()

        # remove first and last message separately
        await (await ctx.channel.fetch_message(arg1)).delete()
        if arg2 != None:
            await (await ctx.channel.fetch_message(arg2)).delete()
        
        # remove rest of the messages
        if arg2 == None:
            await ctx.channel.purge(after=discord.Object(arg1))
        else:
            await ctx.channel.purge(after=discord.Object(arg1), before=discord.Object(arg2))


def setup(bot):
    bot.add_cog(Purge(bot))
