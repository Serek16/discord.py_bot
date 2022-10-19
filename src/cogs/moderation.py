from src.utils.logger import get_logger
import discord
from discord.ext import commands

logger = get_logger(__name__, __name__)


class Moderation(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """When member is banned from one of the bot's servers,
            automatically gets banned on any server where the bot has ban permissions"""

        try:
            banned = await member.guild.fetch_ban(member)
        except discord.NotFound:
            banned = False

        if banned:
            reason = ""
            # Get a ban reason
            ban_entries = await member.guild.bans()
            for ban_entry in ban_entries:
                if ban_entry.user.id == member.id:
                    reason = ban_entry.reason
                    break

            logger.info(
                f"{member.name} ({member.id}) has been banned in {member.guild.name} ({member.guild.id})."
                f" Reason: {reason}")

            user = self.bot.get_user(member.id)

            # Ban a member in every guild that bot is in and delete messages for the last 7 days
            for guild in self.bot.guilds:
                guild: discord.Guild
                try:
                    if guild.id == member.guild.id:
                        await guild.ban(user, reason=reason, delete_message_days=7)
                    else:
                        await guild.ban(user, reason=f"{reason} (banned in {member.guild.name} [{member.guild.id}])",
                                        delete_message_days=7)

                except discord.HTTPException as err:
                    logger.error(err)

    @commands.command()
    @commands.has_role("Administrator")
    async def ban(self, ctx: discord.ext.commands.Context, member_id: int | str, *reason):
        """Ban command which ban a member on every server in the network.

        :param discord.ext.commands.Context ctx: message context
        :param int|str member_id: member's ID
        :param reason: (optional) reason for the ban
        """

        if member_id is None:
            await ctx.send("You have to provide a valid member id.")
            logger.warning(f"You have to provide a valid member id")
            return

        try:
            if type(member_id) is str and member_id.startswith("<@"):
                member_id = int(member_id[:2][:-1])
            else:
                member_id = int(member_id)

        except ValueError:
            await ctx.send("You have to provide a valid member id.")
            logger.warning(f"You have to provide a valid member id. Current value: {id}")
            return

        user = self.bot.get_user(member_id)

        # Ban a member in every guild that bot is in and delete messages for the last 7 days
        for guild in self.bot.guilds:
            guild: discord.Guild
            try:
                reason = ' '.join([''.join(tup) for tup in reason])
                if guild.id == ctx.guild.id:
                    await guild.ban(user, reason=' '.join(reason), delete_message_days=7)
                    await ctx.send(f"Banned user <@{member_id}>")
                else:
                    # Add a note informing on which server a member was originally banned
                    await guild.ban(user, reason=f"{' '.join(reason)} (banned on {ctx.guild.name} [{ctx.guild.id}])",
                                    delete_message_days=7)

                logger.debug(f"User {user.name} banned on {guild.name} ({guild.id})")

            except Exception as err:
                logger.error(err)

    @commands.command()
    @commands.has_role("Administrator")
    async def unban(self, ctx, member_id: int | str):
        """UnBan command which ban a member on every server in the network.

        :param discord.ext.commands.Context ctx: message context
        :param int|str member_id: member's ID
        """

        if member_id is None:
            await ctx.send("You have to provide a valid member id.")
            logger.warning(f"You have to provide a valid member id. Current value: {member_id}")
            return

        try:
            if member_id.startswith("<@"):
                member_id = int(member_id[:2][:-1])
            else:
                member_id = int(member_id)

        except ValueError:
            await ctx.send("You have to provide a valid member id.")
            logger.warning(f"You have to provide a valid member id. Current value: {id}")
            return

        user = self.bot.get_user(member_id)

        # Unban a member in every guild that bot is in
        for guild in self.bot.guilds:
            guild: discord.Guild
            try:
                if guild.id == ctx.guild.id:
                    await guild.unban(user)
                    await ctx.send(f"Unbanned user<@{member_id}>")
                else:
                    # Add a note informing on which server a member was originally unbanned
                    await guild.unban(user, reason=f"(unbanned on {ctx.guild.name} [{ctx.guild.id}])")

                logger.debug(f"User {user.name} unbanned on {guild.name} ({guild.id})")

            except discord.HTTPException as err:
                logger.error(err)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
