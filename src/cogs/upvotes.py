import discord
from discord import Object
from discord.ext import commands

from src.utils.bot_utils import extract_channel_id
from src.utils.config_val_io import GuildSpecificValues
from src.utils.databaseIO import add_upvote, add_downvote, remove_upvote, remove_downvote, get_reaction_list
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)

UPVOTE_EMOJI = "⬆"
DOWNVOTE_EMOJI = "⬇"
LEADERBOARD_MEMBER_LIST_LENGTH = 10


class Upvotes(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        message = await self.bot.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(
            payload.message_id)

        # User can't upvote his own messages.
        if payload.user_id == message.author.id:
            await message.remove_reaction(payload.emoji, Object(payload.user_id))
            return

        await self.__reaction_event(payload.emoji, payload.channel_id, payload.message_id, payload.user_id,
                                    add_upvote, add_downvote)

    @commands.Cog.listener("on_raw_reaction_remove")
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.__reaction_event(payload.emoji, payload.channel_id, payload.message_id, payload.user_id,
                                    remove_upvote, remove_downvote)

    async def __reaction_event(self, emoji: discord.PartialEmoji, channel_id: int, message_id: int,
                               member_id: int, upvote_fun, downvote_fun):
        member = self.bot.get_user(member_id)
        channel = self.bot.get_channel(channel_id)
        author = (await channel.fetch_message(message_id)).author
        if self.__target_channels(channel.id, channel.guild.id):
            if not member.bot:
                if author.id != member.id:
                    logger.debug(f"{member.name} {'added' if upvote_fun == add_upvote else 'removed'} "
                                 f"' {emoji} ' emoji to {author.name} message id: {message_id}")
                    if emoji.name == UPVOTE_EMOJI:
                        upvote_fun(author)
                    elif emoji.name == DOWNVOTE_EMOJI:
                        downvote_fun(author)

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if self.__target_channels(message.channel.id, message.channel.guild.id):

            media_domains = ('https://cdn.discordapp.com/attachments/', 'https://media.discordapp.net/attachments/',
                             'https://discord.com/channels/')

            # If the message contains any attachment, or it is a text with link to a media content
            if message.attachments or any(substring in message.content for substring in media_domains):
                await message.add_reaction("⬆")
                await message.add_reaction("⬇")

    @commands.command()
    async def leaderboard(self, ctx: commands.Context):
        reactions = get_reaction_list(LEADERBOARD_MEMBER_LIST_LENGTH)
        result = ""
        for i, reaction in enumerate(reactions):
            result += f"{i + 1}. <@{reaction['member_id']}> " \
                      f"- upvotes: {reaction['upvotes']}, downvotes: {reaction['downvotes']}\n"

        embed = discord.Embed(title="Top 10 members with the most upvotes", description=result,
                              color=discord.Colour.random())
        await ctx.send(embed=embed)

    @commands.has_role('Administrator')
    @commands.command(name="upvote-channels")
    async def upvote_channels(self, ctx: commands.Context, *args):

        if not args:
            channel_list = ""
            for channel_id in GuildSpecificValues.get(ctx.guild.id, "upvote_channels"):
                channel_list += f'<#{channel_id}> '
            await ctx.send(f"Upvote channels: {channel_list}")
            return

        match args[0]:
            case 'add':
                await self.__add(ctx, args[1:])
            case 'remove':
                await self.__remove(ctx, args[1:])
            case 'remove-all':
                await self.__remove_all(ctx)
            case _:
                await ctx.send(
                    f"There is no such command \"{args[0]}\". Available commands ['add', 'remove', 'remove-all']")
                return

    @staticmethod
    async def __add(ctx: commands.Context, args: tuple):
        """Subcommand "upvote_channels add [channel_id]"""

        if not args or len(args) != 1:
            await ctx.send("You have to provide existing channel")
            return

        try:
            channel_id = extract_channel_id(args[0])
            if ctx.guild.get_channel(channel_id) is None:
                await ctx.send(f"Channel with id {channel_id} doesn't exist")
        except ValueError:
            await ctx.send("You have to provide existing channel")
            return

        cur_channels: list = GuildSpecificValues.get(ctx.guild.id, 'upvote_channels')
        if channel_id not in cur_channels:
            cur_channels.append(channel_id)
            GuildSpecificValues.set(ctx.guild.id, 'upvote_channels', cur_channels)
            await ctx.send(f"<#{channel_id}> channel has been added to the list")
        else:
            await ctx.send(f"<#{channel_id}> already exists in the list")

    @staticmethod
    async def __remove(ctx: commands.Context, args: tuple):
        """Subcommand "upvote_channels remove [channel_id]"""

        if not args or len(args) != 1:
            await ctx.send("You have to provide existing channel")
            return

        try:
            channel_id = extract_channel_id(args[0])
            if ctx.guild.get_channel(channel_id) is None:
                await ctx.send(f"Channel with id {channel_id} doesn't exist")
        except ValueError:
            await ctx.send("You have to provide existing channel")
            return

        cur_channels: list = GuildSpecificValues.get(ctx.guild.id, 'upvote_channels')
        try:
            cur_channels.remove(channel_id)
            GuildSpecificValues.set(ctx.guild.id, 'upvote_channels', cur_channels)
            await ctx.send(f"<#{channel_id}> channel has been removed from the list")
        except ValueError:
            await ctx.send(f"<#{channel_id}> doesn't exist in the list")

    @staticmethod
    async def __remove_all(ctx: commands.Context):
        """Subcommand "upvote_channels remove-all"""

        GuildSpecificValues.set(ctx.guild.id, 'upvote_channels', [])
        await ctx.send("All channels have been removed from the list")

    @staticmethod
    def __target_channels(channel_id: int, guild_id: int) -> bool:
        targeted_channels_id: list = GuildSpecificValues.get(
            guild_id, 'upvote_channels')
        for _id in targeted_channels_id:
            if _id == channel_id:
                return True
        return False


async def setup(bot):
    await bot.add_cog(Upvotes(bot))
