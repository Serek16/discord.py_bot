import discord
from discord.ext import commands

from src.utils.bot_utils import has_role
from src.utils.config_val_io import GuildSpecificValues
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)

ALLOWED_DOMAINS = (
    'https://discord.com',
    'https://media.discordapp.net',
    'https://cdn.discordapp.com',
    'https://tenor.com/view',
    'https://imgur.com'
    'https://www.youtube.com',
    'https://youtu.be',
    'https://www.reddit.com',
    'https://twitter.com',
    'https://open.spotify.com',
)


class NoLinks(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        author = message.author

        if 'http://' in message.content:
            try:
                await message.delete()
                logger.info(
                    f"Removed \"{message.content}\" message from {author.name}#{author.discriminator} due "
                    f"to containing a not secured link.")
            except discord.NotFound:
                # The message was probably removed by some other bot.
                return

        if 'https://' in message.content:
            if has_role(message.guild.get_member(author.id), GuildSpecificValues.get(message.guild.id, 'newbie')):
                if not any(ext in message.content for ext in ALLOWED_DOMAINS):
                    try:
                        await message.delete()
                        logger.info(
                            f"Removed \"{message.content}\" message from "
                            f"{message.author.name}#{message.author.discriminator}"
                            f" due to containing a link from outside of allowed domain list posted by low rank user.")
                    except discord.NotFound:
                        # The message was probably removed by some other bot.
                        return


async def setup(bot):
    await bot.add_cog(NoLinks(bot))
