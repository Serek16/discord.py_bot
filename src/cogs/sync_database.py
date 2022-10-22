import discord

from src.model.member import Member
from src.utils import databaseIO
from src.utils.logger import get_logger
from discord.ext import commands
from src.utils.bot_utils import has_role, get_global, get_id_guild
from src.selfbot.selfbot_utils import fetchMembersLevel
from src.selfbot.discum_bot import DiscumBot

logger = get_logger(__name__, __name__)


class SyncDatabase(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role('Administrator')
    async def sync_database(self, ctx: commands.Context, sync_levels=False):
        """synchronize the presence of members on the server and in the database"""

        await ctx.send("sync_database: Starting")
        logger.info("sync_database: Starting")

        guild = ctx.guild
        guild_members = list(guild.members)

        booster_role_id = get_id_guild('booster', guild.id)
        newbie_role_id = get_id_guild('newbie', guild.id)
        no_newbie_level = get_global('newbie_level')

        discum_bot = DiscumBot(get_global("selfbot_token"))

        db_member_list = databaseIO.get_all_members()
        db_member_count = len(db_member_list)

        for i, db_member in enumerate(db_member_list):

            logger.info(
                f"Checking: {db_member.username} ({db_member.member_id}) [{i}/{db_member_count}]")

            # Check if the member is still on the server
            member = None
            for _member in guild_members:
                if _member.id == db_member.member_id:
                    member = _member
                    guild_members.remove(member)

            # If member is still on the server
            if member is not None:
                logger.info(f" {member.name} is still on the server")
                db_member.member_left = False

                if sync_levels:
                    db_member.level = fetchMembersLevel(member, discum_bot)
                    logger.debug(f"Fetched level: {db_member.level} from user {db_member.username}")
                databaseIO.save_member(db_member)

                if db_member.level >= no_newbie_level:
                    if has_role(member, newbie_role_id):
                        await member.remove_roles(discord.Object(newbie_role_id))
                else:
                    # If member's level is lower than minimal level required to no longer be a newbie, and he
                    # isn't a booster, nor he's a bot and doesn't have newbie role already
                    if has_role(member, newbie_role_id) is False \
                            and has_role(member, booster_role_id) is False \
                            and member.bot is False:
                        await member.add_roles(discord.Object(newbie_role_id))

            # If member is no loner on the server
            else:
                logger.info(f" {db_member.username} is no longer on the server")
                db_member.member_left = True
                databaseIO.save_member(db_member)

        logger.info("Searching through members that are on the server but are not in the database")

        # Search through members that are on the server but are not in the database
        for i, member in enumerate(guild_members):
            logger.info(
                f"Member {member.name} ({member.id}) not in the database [{i}/{len(guild_members)}]")

            level = fetchMembersLevel(member, discum_bot)
            logger.debug(f"Fetched level: {level} from user: {member.name}")

            if has_role(member, 'booster_id') is False and member.bot is False and level < no_newbie_level:
                try:
                    await member.add_roles(discord.Object(newbie_role_id))
                except discord.HTTPException as error:
                    # Member probably left the server while syncing was on
                    logger.error(error)
                    continue

            databaseIO.save_member(Member(member.id, member.name, level))

        logger.info("sync_database: Done")
        await ctx.send("sync_database: Done")


async def setup(bot):
    await bot.add_cog(SyncDatabase(bot))
