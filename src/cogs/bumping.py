import discord
from discord.ext import tasks, commands

from src.selfbot.discum_bot import DiscumBot
from src.selfbot.slash_command import SlashCommand
from src.utils.bot_utils import get_global
from src.utils.config_val_io import GuildSpecificVals, AllGuildVals
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


class Bumping(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.bump.start()

    @tasks.loop(minutes=15.0)
    async def bump(self):
        discum_bot = DiscumBot(get_global("selfbot_token"))
        for guild_id, bump_channel_id in AllGuildVals.get('bump_channel'):
            discum_bot.sendSlashCommand(SlashCommand(guild_id, bump_channel_id, get_global('disboard_id'), 'bump'))

    @commands.command()
    @commands.has_role('Administrator')
    async def bump_channel(self, ctx: commands.Context, channel: str):

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

        GuildSpecificVals.save(ctx.guild.id, 'bump_channel', channel_id)
        logger.info(f"Successfully set {channel_id} as bumping channel")
        await ctx.send(f"Successfully set <#{channel_id}> as bumping channel")


async def setup(bot):
    await bot.add_cog(Bumping(bot))
