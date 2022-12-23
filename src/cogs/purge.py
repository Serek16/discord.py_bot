from src.utils.logger import get_logger
from discord.ext import commands
from datetime import datetime
import discord

logger = get_logger(__name__, __name__)


class Purge(commands.Cog):

    def __init__(self, bot):
        self.bot: discord.Client = bot

    @staticmethod
    def __is_text(message: discord.Message) -> bool:
        """Check if given message is a text message.\n
            If it's a link leading to one of the allowed domains it's not considered a text message"""

        allowed_domains = ("https://cdn.discordapp.com/attachments/", "https://discord.com/channels/",
                           "https://tenor.com/view/")
        if message.attachments:
            return False
        for domain in allowed_domains:
            if domain in message.content:
                return False
        return True

    @commands.command()
    @commands.has_role('staff')
    async def purge(self, ctx: commands.Context, arg1, arg2=None, only_text=False):
        """Remove messages from the channel on which the command was used
            if arg2 is None, then delete all messages to message with arg1 id.
            Otherwise, delete all messages from message with id arg1 to message with id arg2"""

        if only_text is False:
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
    @commands.has_role('staff')
    async def purgeText(self, ctx: commands.Context, arg1, arg2=None):
        """Remove text messages from the channel on which the command was used
            if arg2 is None, then delete all messages to message with arg1 id.
            Otherwise, delete all messages from message with id arg1 to message with id arg2"""

        logger.info(f"{ctx.author} used purgeText in {ctx.channel.name}")
        await self.purge(ctx, arg1, arg2, only_text=True)

    @commands.command()
    @commands.has_role('staff')
    async def purgeCLI(self, ctx: commands.Context, *args):
        """Remove messages from the channel providing arguments
            -f --from (optional) ID of the message from which purge will begin
            -t --to ID of the message where purge ends
            -u --user ID of user whose only messages will be deleted
            --only-text (optional) Delete only text messages
            -l (optional) How many messages take into account. Default value is 100
        """

        from_date = ctx.message.created_at
        to_date = None
        user_id = None
        only_text = False
        limit = 100

        for arg in args:
            prefix: str = arg[:2]
            match(prefix):
                case '-f' | '--from':
                    try:
                        from_date = (await ctx.fetch_message(int(arg[3:]))).created_at
                    except discord.NotFound:
                        await ctx.send(f"Message with id {arg[3:]} doesn't exist")
                        return

                case '-t' | '--to':
                    try:
                        to_date = (await ctx.fetch_message(int(arg[3:]))).created_at
                    except discord.NotFound:
                        await ctx.send(f"Message with id {arg[3:]} doesn't exist")
                        return

                case '-u' | '--user':
                    user_id = int(arg[3:])
                    if self.bot.get_user is None:
                        await ctx.send(f"user with id {arg[3:]} doesn't exist")

                case '--only-text':
                    only_text = True

                case '-l' | '--limit':
                    limit = int(arg[3:])

        # argument to_date is necessary for the command to work
        if to_date is None:
            await ctx.send("You have to specify -t <message-id>. Where message-id is ID of the message where purge ends")
            logger.error("You have to specify -t <message-id>. Where message-id is ID of the message where purge ends")
            return

        await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, check=lambda msg: self.__filter_message(msg, from_date, to_date, user_id, only_text))

        logger.info(f"purged {len(purged)} messages")


    @staticmethod
    def __filter_message(msg: discord.Message, from_date: datetime, to_date: datetime, user_id: int, only_text: bool) -> bool:
        # If the message is younger than purge begin message 
        if msg.created_at >= from_date:
            return False
        
        # If the message is older than the purge end message
        if to_date is not None and msg.created_at <= to_date:
            return False

        # If the message isn't a text
        if only_text and not Purge.__is_text(msg):
            return False

        # If the message isn't written by a certain user
        if user_id is not None and msg.author.id != user_id:
            return False

        return True


async def setup(bot):
    await bot.add_cog(Purge(bot))
