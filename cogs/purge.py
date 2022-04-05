from discord.ext import commands
import discord
import sys  

sys.path.append('../')
from logger import get_logger

logger = get_logger(__name__)


class Purge(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    def __is_text(self, message):
        allowed_domains = ("https://cdn.discordapp.com/attachments/", "https://tenor.com/view/", "https://cdn.discordapp.com/attachments/")
        if message.attachments != []:
            return False
        for domain in allowed_domains:
            if domain in message.content:
                return False
        return True

    @commands.command()
    @commands.has_role(910458855023083577)
    async def purge(self, ctx, arg1, arg2=None, only_text=False):
        '''Remove messages from the channel on which the command was used'''
        
        if only_text == False:
            logger.info(f"{ctx.author} used purge in {ctx.channel.name}")

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
            await ctx.channel.purge(after=discord.Object(arg1), check=lambda m: (only_text == True and self.__is_text(m) == True))
        else:
            await ctx.channel.purge(after=discord.Object(arg1), before=discord.Object(arg2), check=lambda m: (only_text == True and self.__is_text(m) == True))

    
    @commands.command()
    @commands.has_role(910458855023083577)
    async def purgeText(self, ctx, arg1, arg2=None):
        logger.info(f"{ctx.author} used purgeText in {ctx.channel.name}")
        await self.purge(ctx, arg1, arg2, True)


def setup(bot):
    bot.add_cog(Purge(bot))
