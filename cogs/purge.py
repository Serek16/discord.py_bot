from discord.ext import commands
import discord
import sys  
import numpy as np

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
    @commands.has_role(964219616371044402)
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


        to_delete_not_verified = []

        # add user's command message. If the second argument isn't provided this message will be added to the list later
        if arg2 != None:
            to_delete_not_verified.append(ctx.message)

        # add first and last message (channel.history doesn't include them)
        to_delete_not_verified.append(await ctx.channel.fetch_message(arg1))
        if arg2 != None:
            to_delete_not_verified.append(await ctx.channel.fetch_message(arg2))

        # add the rest of the messages
        if arg2 == None:
            to_delete_not_verified += await ctx.channel.history(after=discord.Object(arg1)).flatten()
        else:
            to_delete_not_verified += await ctx.channel.history(after=discord.Object(arg1), before=discord.Object(arg2)).flatten()


        # if you want to only remove text messages
        to_delete = []
        if only_text == True:
            for message in to_delete_not_verified:
                if (self.__is_text(message) == True):
                    to_delete.append(message)
        else:
            to_delete = to_delete_not_verified


        for chunk in list(self.__divide_chunks(to_delete, 100)) :
            print(f"chunk size: {len(chunk)}")
            await ctx.channel.delete_messages(chunk)


    def __divide_chunks(self, l, n):
        for i in range(0, len(l), n): 
            yield l[i:i + n]

    
    @commands.command()
    @commands.has_role(964219616371044402)
    async def purgeText(self, ctx, arg1, arg2=None):
        logger.info(f"{ctx.author} used purgeText in {ctx.channel.name}")
        await self.purge(ctx, arg1, arg2, True)


def setup(bot):
    bot.add_cog(Purge(bot))
