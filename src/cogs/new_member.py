import datetime
import discord
from src.model.member import Member
from src.utils.databaseIO import get_member_by_id, save_member
from src.utils.logger import get_logger
from discord.ext import commands
from src.utils.config_val_io import AggregatedGuildValues, GlobalValues, GuildSpecificValues

logger = get_logger(__name__, __name__)


class NewMember(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Add each member that joins the server to the database"""

        # Focus only on the main server
        if member.guild.id != AggregatedGuildValues.get('guild_id')[0][1]:
            return

        logger.info(f"Member {member.name} ({member.id}) joined the server")

        newbie = True

        db_member = get_member_by_id(member.id)

        # Member doesn't exist in the database
        if db_member is None:
            logger.info(f"{member.name}: no record in the database")
            save_member(Member(member.id, member.name))

        # Member exists in the database
        else:
            logger.info(f"{member.name}: already exists in the database")
            db_member.member_left = False
            db_member.last_join = datetime.datetime.now()
            save_member(db_member)

            # If level is greater than or equals minimal required level to not be a newbie anymore
            if db_member.level >= GlobalValues.get('newbie_level'):
                newbie = False

        guild = member.guild
        if newbie is True and member.bot is False:
            await member.add_roles(guild.get_role(GuildSpecificValues.get(guild.id, 'newbie')))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Update the database when a member leave the server"""

        # Focus only on the main server
        if member.guild.id != AggregatedGuildValues.get('guild_id')[0]:
            return

        logger.info(f"Member {member.name} ({member.id}) left the server")

        db_member = get_member_by_id(member.id)

        # Member doesn't exist in the database
        if db_member is None:
            logger.info(f"{member.name}: no record in the database")
            save_member(Member(member.id, member.name, member_left=True))

        # Member exists in the database
        else:
            logger.info(f"{member.name}: already exists in the database")
            db_member.member_left = True
            save_member(db_member)


async def setup(bot):
    await bot.add_cog(NewMember(bot))
