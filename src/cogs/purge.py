import argparse
import shlex

import discord
from discord.ext import commands

from src.utils.bot_utils import extract_user_id, extract_channel_id
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


class Purge(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command()
    @commands.has_role('staff')
    async def purge(self, ctx: commands.Context, arg1, arg2=None, only_text=False):
        """Remove messages from the channel on which the command is used.
            If arg2 is None, then bot deletes all messages to the message with id arg1.
            Otherwise, delete all messages starting from the message with id arg1 to the message with id arg2"""

        # Check if member has permission himself to remove messages in specified channel
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send(f"You don't have persmissions to use this command in this channel")
            return

        if only_text is False:
            logger.info(f"{ctx.author} used purge in {ctx.channel.name}")

        from_datetime = ctx.message.created_at
        to_datetime = (await ctx.fetch_message(arg1)).created_at

        if arg2 is not None:
            from_datetime = to_datetime
            to_datetime = (await ctx.fetch_message(arg2)).created_at

        await ctx.message.delete()

        purged_total_len = 0
        chunk_size = 100
        while True:
            purged = await ctx.channel.purge(limit=chunk_size,
                                             before=from_datetime,
                                             after=to_datetime,
                                             oldest_first=False,
                                             check=lambda msg: self.__filter_message(msg, only_text=only_text))
            purged_total_len += len(purged)

            # If last purged message is younger than date from to_datetime. It can mean that 100 (default chunk_size)
            # messages were purged and program is ready to purge more, till it reach to_datetime value from last message
            if len(purged) > 0:
                next_message = \
                    [message async for message in ctx.channel.history(limit=1, before=purged[-1].created_at)][0]
                if next_message.created_at == to_datetime:
                    break

            chunk_size *= 2
            if chunk_size >= 4000:  # Don't overload Discord's API
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
            -f --from ID of the message from which purge will begin. Default is the time when the command was used
            -t --to ID of the message where purge ends. (Optional)
            -u --user ID of user whose only messages will be deleted. (Optional)
            --only-text Delete only text messages. Default is False
            -l --limit How many messages should be removed. If LIMIT and TO is not specified LIMIT is 100
            -c --channel Which channel should be purged. Default channel is where command was used
        """

        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--from", dest="_from", type=int,
                            help="ID of the message from which purge will begin. Default is the time when the "
                                 " was used")
        parser.add_argument("-t", "--to", dest="to", type=int,
                            help="ID of the message where purge ends. (Optional)")
        parser.add_argument("-u", "--user", dest="user", type=str,
                            help="ID of user whose only messages will be deleted. (Optional)")
        parser.add_argument("--only-text", dest="only_text", action="store_true",
                            help="Delete only text messages. Default is False")
        parser.add_argument("-l", "--limit", dest="limit", type=int,
                            help="How many messages should be removed. If LIMIT and TO is not specified LIMIT is 100")
        parser.add_argument("-c", "--channel", dest="channel", type=str,
                            help="Which channel should be purged. Default channel is where command was used")

        try:
            args = parser.parse_args(shlex.split(args))
        except argparse.ArgumentError as e:
            logger.error(e)
            await ctx.send(e.message)
            return
        except SystemExit:
            # When --help is used
            await ctx.send(parser.format_help())
            return

        channel = ctx.channel
        # If user specify channel argument check if channel even exists
        if args.channel is not None:
            try:
                channel_id = extract_channel_id(args.channel)
            except ValueError:
                await ctx.send(
                    f"\"{args.user}\" is invalid. You have to mention existing channel ot provide valid channel id")
                return
            channel = ctx.guild.get_channel(channel_id)
            if channel is None:
                await ctx.send(f"User with id {args.user} doesn't exist")
                return

        # Check if member has permission himself to remove messages in specified channel
        if not channel.permissions_for(ctx.author).manage_messages:
            await ctx.send(f"You don't have persmissions to use this command in <#{channel.id}>")
            return

        from_datetime = None
        # When argument _from is not None, validate if message with given id exits
        if args._from is not None:
            try:
                from_datetime = (await channel.fetch_message(args._from)).created_at
            except discord.NotFound:
                await ctx.send(f"Message with id {args._from} doesn't exist")
                return

        to_datetime = None
        # When argument to is not None, validate if message with given id exits
        if args.to is not None:
            try:
                to_datetime = (await channel.fetch_message(args.to)).created_at
            except discord.NotFound:
                await ctx.send(f"Message with id {args.to} doesn't exist")
                return

        user_id = None
        # When arg user is not None, validate if user with given id exits
        if args.user is not None:
            try:
                user_id = extract_user_id(args.user)
            except ValueError:
                await ctx.send(
                    f"\"{args.user}\" is invalid. You have to mention existing user ot provide valid user id")
                return
            if self.bot.get_user(user_id) is None:
                await ctx.send(f"User with id {args.user} doesn't exist")
                return

        if args.limit is None and to_datetime is None:
            args.limit = 100

        await ctx.message.delete()

        purged_total_count = 0
        chunk_size = args.limit or 100
        while True:
            purged = await channel.purge(limit=chunk_size,
                                         before=from_datetime,
                                         after=to_datetime,
                                         oldest_first=False,
                                         check=lambda msg: self.__filter_message(msg, user_id, args.only_text))

            purged_total_count += len(purged)

            # If last purged message is younger than date from to_datetime. It can mean that 100 (default chunk_size)
            # messages were purged and program is ready to purge more, till it reach to_datetime value from last message
            if len(purged) > 0:
                next_message = \
                    [message async for message in channel.history(limit=1, before=purged[-1].created_at)][0]
                if next_message.created_at == to_datetime:
                    break

            if args.limit is not None and args.limit <= purged_total_count:
                break

            # Double the chunk_size. Sometimes no messages can be purged beacsue of limit value doesn't allow to
            # reach messages older than from_datetime date
            chunk_size *= 2
            if chunk_size >= 4000:  # Don't overload Discord's API
                break

        logger.info(f"purged {purged_total_count} messages")

    @staticmethod
    def __filter_message(msg: discord.Message, user_id: int = None, only_text: bool = False) -> bool:

        # If the message isn't a text
        if only_text and not Purge.__is_text(msg):
            return False

        # If the message isn't written by a certain user
        if user_id is not None and msg.author.id != user_id:
            return False

        return True

    @staticmethod
    def __is_text(message: discord.Message) -> bool:
        allowed_domains = ('https://cdn.discordapp.com/attachments/', 'https://discord.com/channels/',
                           'https://media.discordapp.net/attachments/', 'https://tenor.com/view/')
        if message.attachments:
            return False
        for domain in allowed_domains:
            if domain in message.content:
                return False
        return True


async def setup(bot):
    await bot.add_cog(Purge(bot))
