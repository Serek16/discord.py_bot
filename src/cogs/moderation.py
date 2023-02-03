import discord
from discord.ext import commands

from src.utils.bot_utils import extract_user_id
from src.utils.databaseIO import get_member_by_id, save_member
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


class Moderation(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """When member is banned from one of the bot's servers,
            automatically gets banned on any server where the bot has ban permissions."""

        # Check if user was banned or if he left on his own
        try:
            ban_entry = await member.guild.fetch_ban(member)
            reason = ban_entry.reason
        except discord.NotFound:
            # User wasn't banned
            return

        logger.info(
            f"{member.name}#{member.discriminator} @{member.id} has been banned in "
            f"{member.guild.name} @{member.guild.id}. Reason: {reason}.")

        user = self.bot.get_user(member.id)
        await self.ban_user(user, reason, member.guild)

        # Change member status in the database
        db_member = get_member_by_id(member.id)
        db_member.member_left = True
        db_member.is_banned = True
        save_member(db_member)

    @commands.command()
    @commands.has_role("Administrator")
    async def ban(self, ctx: commands.Context, member_id: int | str, *, reason: str):
        """Ban command which ban a member on every server in the network.

        :param discord.ext.commands.Context ctx: message context
        :param int|str member_id: member's ID
        :param reason: (optional) the reason for the ban
        """

        try:
            member_id = extract_user_id(member_id)
        except ValueError:
            await ctx.send("You have to provide a valid member id.")
            logger.warning(f"You have to provide a valid member id. Current value: {id}")
            return

        user = self.bot.get_user(member_id)
        await self.ban_user(user, reason, ctx.guild)

        # Change member status in the database
        db_member = get_member_by_id(member_id)
        db_member.member_left = True
        db_member.is_banned = True
        save_member(db_member)

    @commands.command()
    @commands.has_role("Administrator")
    async def unban(self, ctx: commands.Context, member_id: int | str, *, reason: str):
        """UnBan command which ban a member on every server in the network.

        :param discord.ext.commands.Context ctx: message context
        :param int|str member_id: member's ID
        :param str reason: (optional) the reason of the unban
        """

        try:
            member_id = extract_user_id(member_id)
        except ValueError:
            await ctx.send("You have to provide a valid member id.")
            logger.warning(f"You have to provide a valid member id. Current value: {id}")
            return

        user = self.bot.get_user(member_id)
        await self.unban_user(user, reason, ctx.guild)
        await ctx.send(f"Unbanned user<@{member_id}>")

        # Change member status in the database
        db_member = get_member_by_id(member_id)
        db_member.is_banned = False
        save_member(db_member)

    async def ban_user(self, user: discord.User, reason: str = None, guild_of_origin: discord.Guild = None) -> None:
        """Ban a member in every guild that bot is in and delete messages for the last 7 days."""

        for guild in self.bot.guilds:
            try:
                # If guild_od_origin is None don't mention on what guild the unban command was used
                # on the rest of the guilds
                if guild.id == guild_of_origin.id or guild_of_origin is None:
                    await guild.ban(user, reason=f"{reason}", delete_message_days=7)
                else:
                    # Add a note informing on which server a member was originally banned
                    await guild.ban(
                        user,
                        reason=f"reason: {reason}\nbanned on {guild_of_origin.name} @{guild_of_origin.id}",
                        delete_message_days=7)

                logger.debug(f"User {user.name}#{user.discriminator} banned on {guild.name} @{guild.id}")

            except Exception as err:
                logger.error(err)

    async def unban_user(self, user: discord.User, reason: str = None, guild_of_origin: discord.Guild = None):
        """Unban a member in every guild that bot is in"""

        for guild in self.bot.guilds:
            try:
                # If guild_od_origin is None don't mention on what guild the unban command was used
                # on the rest of the guilds
                if guild.id == guild_of_origin.id or guild_of_origin is None:
                    await guild.unban(user, reason=reason)
                else:
                    # Add a note informing on which server a member was originally unbanned
                    await guild.unban(
                        user,
                        reason=f"reason: {reason}\nunbanned on {guild_of_origin.name} @{guild_of_origin.id}")

                logger.debug(f"User {user.name}#{user.discriminator} unbanned on {guild.name} @{guild.id}.")

            except discord.HTTPException as err:
                logger.error(err)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
