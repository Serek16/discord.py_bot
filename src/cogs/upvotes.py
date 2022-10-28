import discord

from src.utils.bot_utils import get_id_guild
from src.utils.config_val_io import GuildSpecificVals
from src.utils.databaseIO import add_upvote, add_downvote, remove_upvote, remove_downvote, get_reaction_list
from src.utils.logger import get_logger
from discord.ext import commands

logger = get_logger(__name__, __name__)

UPVOTE_EMOJI = "⬆"
DOWNVOTE_EMOJI = "⬇"


class Upvotes(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
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
        if targetChannels(channel.id, channel.guild.id):
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
        if targetChannels(message.channel.id, message.channel.guild.id):
            if message.attachments or message.content.startswith('https://cdn.discordapp.com/attachments/'):
                await message.add_reaction("⬆")
                await message.add_reaction("⬇")

    @commands.command()
    async def leaderboard(self, ctx: commands.Context):
        reactions = get_reaction_list(10)
        result = ""
        for i, reaction in enumerate(reactions):
            result += f"{i + 1}. <@{reaction['member_id']}> " \
                      f"- upvotes: {reaction['upvotes']}, downvotes: {reaction['downvotes']}\n"
        await ctx.send(result)

    @commands.has_role('Administrator')
    @commands.command()
    async def upvote_channels(self, ctx: commands.Context, command: str = None, channel: str = None):

        logger.info(
            f"command upvote_channels command: {command} channel: {channel} used"
            f" in {ctx.channel.name} by {ctx.author.name}")

        if command is None:
            channels = ''
            for channel_id in GuildSpecificVals.get(ctx.guild.id, 'upvote_channels'):
                channels += f'<#{channel_id}> '
            logger.debug(f"upvote channels: {channels}")
            await ctx.send(f"upvote channels: {channels}")
            return

        _commands = ['add', 'remove', 'remove-all']
        if command not in _commands:
            logger.error(f"There is no such command \"{command}\"")
            await ctx.send(f"There is no such command \"{command}\". Available commands {_commands}")
            return

        if command == 'remove-all':
            self.__remove_all(ctx.guild.id)
            return

        channel_id = channel
        if channel_id.startswith("<#"):
            channel_id = channel_id[2:-1]

        try:
            channel_id = int(channel_id)
        except ValueError:
            logger.error(f"{channel} is not a valid channel id")
            await ctx.send("You have to provide valid channel id")
            return

        if self.bot.get_channel(channel_id) is None:
            logger.error(f"{channel} does not exist")
            await ctx.send(f"{channel} does not exist")
            return

        match command:
            case 'add':
                if not self.__add(ctx.guild.id, channel_id):
                    await ctx.send(f"Channel <#{channel_id}> already exist in the list")
            case 'remove':
                if not self.__remove(ctx.guild.id, channel_id):
                    await ctx.send(f"No such channel in the list <#{channel_id}>")

    def __add(self, guild_id: int, channel_id: int):
        cur_channels: list = GuildSpecificVals.get(guild_id, 'upvote_channels')
        if channel_id not in cur_channels:
            cur_channels.append(channel_id)
            GuildSpecificVals.save(guild_id, 'upvote_channels', cur_channels)
            return True
        return False

    def __remove(self, guild_id: int, channel_id: int):
        cur_channels: list = GuildSpecificVals.get(guild_id, 'upvote_channels')
        try:
            cur_channels.remove(channel_id)
            GuildSpecificVals.save(guild_id, 'upvote_channels', cur_channels)
            return True
        except ValueError:
            return False

    def __remove_all(self, guild_id: int):
        GuildSpecificVals.save(guild_id, 'upvote_channels', [])


async def setup(bot):
    await bot.add_cog(Upvotes(bot))


def targetChannels(channel_id: int, guild_id: int) -> bool:
    targeted_channels_id: list = GuildSpecificVals.get(guild_id, 'upvote_channels')
    for _id in targeted_channels_id:
        if _id == channel_id:
            return True
    return False
