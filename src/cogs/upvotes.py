import discord

from src.utils.bot_utils import get_id_guild
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
    async def leaderboard(self, ctx):
        reactions = get_reaction_list(10)
        result = ""
        for i, reaction in enumerate(reactions):
            result += f"{i}. <@{reaction['member_id']}> " \
                      f"- upvotes: {reaction['upvotes']}, downvotes: {reaction['downvotes']}\n"
        await ctx.send(result)


async def setup(bot):
    await bot.add_cog(Upvotes(bot))


def targetChannels(channel_id: int, guild_id: int) -> bool:
    targeted_channels_id = get_id_guild('upvote_channels', guild_id)
    for _id in targeted_channels_id:
        if _id == channel_id:
            return True
    return False
