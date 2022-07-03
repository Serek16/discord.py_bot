from logger import get_logger
from discord.ext import commands
import sys
from config import config

sys.path.append('../')

logger = get_logger(__name__, __name__)


class Purge(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def __is_text(self, message):
        '''Check if give message is a text message.\n
            If it's a link leading to one of the allowed domains it's not consifered a text message'''
        
        allowed_domains = ("https://cdn.discordapp.com/attachments/", "https://discord.com/channels/",
                           "https://tenor.com/view/")
        if message.attachments != []:
            return False
        for domain in allowed_domains:
            if domain in message.content:
                return False
        return True

    @commands.command()
    @commands.has_role(int(config("guild_ids")['staff']))
    async def purge(self, ctx, arg1, arg2=None, only_text=False):
        '''Remove messages from the channel on which the command was used
            if arg2 is None, then delete all messages to message with arg1 id.
            Otherwise delete all messages from message with id arg1 to message with id arg2'''

        if only_text == False:
            logger.info(f"{ctx.author} used purge in {ctx.channel.name}")

        dates_before = (await ctx.fetch_message(arg1)).created_at
        if arg2 is not None:
            dates_after = dates_before
            dates_before = (await ctx.fetch_message(arg2)).created_at

        await ctx.message.delete()
        purged = await ctx.channel.purge(limit=1000, check=lambda msg:
                                         (dates_before <= msg.created_at) and
                                         (arg2 is None or dates_after >= msg.created_at) and
                                         (not only_text or self.__is_text(msg)))

        logger.info(f"purged {len(purged)} messages")

    @commands.command()
    @commands.has_role(int(config("guild_ids")['staff']))
    async def purgeText(self, ctx, arg1, arg2=None):
        '''Remove text messages from the channel on which the command was used
            if arg2 is None, then delete all messages to message with arg1 id.
            Otherwise delete all messages from message with id arg1 to message with id arg2'''

        logger.info(f"{ctx.author} used purgeText in {ctx.channel.name}")
        await self.purge(ctx, arg1, arg2, True)


def setup(bot):
    bot.add_cog(Purge(bot))
