import argparse
import shlex
from datetime import datetime

import discord
from discord.ext import commands

from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


class Purge(commands.Cog):

    def __init__(self, bot):
        self.bot: discord.Client = bot

    @staticmethod
    def __is_text(message: discord.Message) -> bool:
        """Check if given message is a text message.\n
            If it's a link leading to one of the allowed domains it's not considered a text message"""

        allowed_domains = ('https://cdn.discordapp.com/attachments/', 'https://discord.com/channels/',
                           'https://media.discordapp.net/attachments/', 'https://tenor.com/view/')
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

        from_datetime = ctx.message.created_at
        to_datetime = (await ctx.fetch_message(arg1)).created_at

        if arg2 is not None:
            from_datetime = to_datetime
            to_datetime = (await ctx.fetch_message(arg2)).created_at

        await ctx.message.delete()

        purged_total_len = 0
        while True:
            purged = await ctx.channel.purge(limit=100,
                                             check=lambda msg: self.__filter_message(msg, from_datetime, to_datetime,
                                                                                     only_text=only_text))
            purged_total_len += len(purged)

            # Break the loop if the last purged message is as old as we intended to. If not, keep purging, take next
            # 100 messages
            if purged[-1].created_at <= to_datetime:
                break

        logger.info(f"purged {purged_total_len} messages")

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
    async def purgeCLI(self, ctx: commands.Context, *, args: str):
        """Remove messages from the channel providing arguments
            -f --from (optional) ID of the message from which purge will begin
            -t --to ID of the message where purge ends
            -u --user ID of user whose only messages will be deleted
            --only-text (optional) Delete only text messages
            -l --limit How many messages will be taken from chat history into account
        """

        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--from", dest="_from", type=int)
        parser.add_argument("-t", "--to", dest="to", type=int)
        parser.add_argument("-u", "--user", dest="user", type=int)
        parser.add_argument("--only-text", dest="only_text", action="store_true")
        parser.add_argument("-l", "--limit", dest="limit", default=100, type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            logger.error(e)
            return

        # When arg from is not None, validate if message with given id exits
        if args._from is None:
            from_datetime = ctx.message.created_at
        else:
            try:
                from_datetime = (await ctx.fetch_message(args._from)).created_at
            except discord.NotFound:
                await ctx.send(f"Message with id {args._from} doesn't exist")
                return

        # Argument to_datetime is necessary for the command to work
        try:
            to_datetime = (await ctx.fetch_message(args.to)).created_at
        except discord.NotFound:
            await ctx.send(
                "You have to specify -t <message-id>. Where <message-id> is ID of the message where purge ends")
            logger.error(
                "You have to specify -t <message-id>. Where <message-id> is ID of the message where purge ends")
            return

        # When arg user is not None, validate if user with given id exits
        if args.user is not None:
            if self.bot.get_user(args.user) is None:
                await ctx.send(f"User with id {args.user} doesn't exist")
                return

        await ctx.message.delete()

        purged = await ctx.channel.purge(limit=args.limit,
                                         check=lambda msg: self.__filter_message(msg, from_datetime, to_datetime,
                                                                                 args.user, args.only_text))

        logger.info(f"purged {len(purged)} messages")

    @staticmethod
    def __filter_message(msg: discord.Message, from_datetime: datetime = datetime.now(), to_datetime: datetime = None,
                         user_id: int = None, only_text: bool = False) -> bool:
        # If the message is younger than the purge begin message
        if msg.created_at >= from_datetime:
            return False

        # If the message is older than the purge end message
        if to_datetime is not None and msg.created_at <= to_datetime:
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
