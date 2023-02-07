import discord
from discord.ext import tasks, commands

from src.selfbot.discum_bot import DiscumBot
from src.selfbot.slash_command import SlashCommand
from src.utils.bot_utils import extract_channel_id
from src.utils.config_val_io import AggregatedGuildValues, GuildSpecificValues, GlobalValues
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


class Bumping(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.selfbot = DiscumBot(GlobalValues.get("selfbot_token"))
        self.bump.start()

    @tasks.loop(minutes=15.0)
    async def bump(self):
        for guild_id, bump_channel_id in AggregatedGuildValues.get('bump_channel'):
            self.selfbot.send_slash_command(
                SlashCommand(guild_id, bump_channel_id, GlobalValues.get('disboard_id'), 'bump'))

    @commands.command()
    @commands.has_role('Administrator')
    async def bump_channel(self, ctx: commands.Context, channel: str):
        try:
            channel_id = extract_channel_id(channel)
        except ValueError:
            logger.error(f"{channel} is not a valid channel id")
            await ctx.send("You have to provide valid channel id")
            return

        if self.bot.get_channel(channel_id) is None:
            logger.error(f"{channel} does not exist")
            await ctx.send(f"{channel} does not exist")
            return

        GuildSpecificValues.set(ctx.guild.id, 'bump_channel', channel_id)
        logger.info(f"Successfully set {channel_id} as bumping channel")
        await ctx.send(f"Successfully set <#{channel_id}> as bumping channel")


async def setup(bot):
    await bot.add_cog(Bumping(bot))
