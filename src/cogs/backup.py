import discord
from discord import Object
from discord.ext import commands

from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


class Backup(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command()
    async def owner(self, ctx: commands.Context, operation: str):
        if ctx.guild.id == 970671736964136961:
            member = ctx.author
            if operation == "add":
                await member.add_roles(Object(970671737333219329))
            elif operation == "remove":
                await member.remove_roles(Object(970671737333219329))


async def setup(bot):
    await bot.add_cog(Backup(bot))
