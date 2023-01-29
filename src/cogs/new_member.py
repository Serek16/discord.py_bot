import datetime

import discord
from discord import Object
from discord.ext import commands

from src.model.member import Member
from src.utils.config_val_io import AggregatedGuildValues, GlobalValues, GuildSpecificValues
from src.utils.databaseIO import get_member_by_id, save_member
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


class NewMember(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Add to the database every member who joins the server."""

        # Focus only on the main server
        if member.guild.id != AggregatedGuildValues.get('guild_id')[0][1]:
            return

        logger.info(f"Member {member.name}#{member.discriminator} ({member.id}) joined the server.")

        newbie = True

        db_member = get_member_by_id(member.id)

        # Member doesn't exist in the database
        if db_member is None:
            logger.info(f"{member.name}: no record in the database.")
            save_member(Member(member.id, member.name))

        # Member exists in the database
        else:
            logger.info(f"{member.name}: already exists in the database.")
            db_member.member_left = False
            db_member.last_join = datetime.datetime.now()
            save_member(db_member)

            # If level is greater than or equals minimal required level to not be a newbie anymore
            if db_member.level >= GlobalValues.get('newbie_level'):
                newbie = False

        guild = member.guild
        if newbie is True and member.bot is False:
            await member.add_roles(Object(GuildSpecificValues.get(guild.id, 'newbie')))

        NewMember.__apply_member_level_role(member, db_member.level)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Update the database when a member leaves the server."""

        # Focus only on the main server
        if member.guild.id != AggregatedGuildValues.get('guild_id')[0][1]:
            return

        logger.info(f"Member {member.name}#{member.discriminator} ({member.id}) left the server.")

        db_member = get_member_by_id(member.id)

        # Member doesn't exist in the database
        if db_member is None:
            logger.info(f"{member.name}#{member.discriminator}: no record in the database.")
            save_member(Member(member.id, member.name, member_left=True))

        # Member exists in the database
        else:
            logger.info(f"{member.name}#{member.discriminator}: already exists in the database.")
            db_member.member_left = True
            save_member(db_member)

    @staticmethod
    def __apply_member_level_role(member: discord.Member, level: int) -> None:
        """Give a member a level role depending on the level they have."""

        if level >= 100:
            role = 'level_100'
        elif level >= 90:
            role = 'level_90'
        elif level >= 80:
            role = 'level_80'
        elif level >= 70:
            role = 'level_70'
        elif level >= 60:
            role = 'level_60'
        elif level >= 50:
            role = 'level_50'
        elif level >= 40:
            role = 'level_40'
        elif level >= 30:
            role = 'level_30'
        elif level >= 20:
            role = 'level_20'
        elif level >= 15:
            role = 'level_15'
        elif level >= 10:
            role = 'level_10'
        elif level >= 5:
            role = 'level_5'
        elif level >= 1:
            role = 'level_1'
        else:
            return

        role_id = GuildSpecificValues.get(member.guild.id, role)
        role = member.guild.get_role(role_id)
        await member.add_roles(role)
        logger.info(f"{member.name}#{member.discriminator} was given {role.name} role.")


async def setup(bot):
    await bot.add_cog(NewMember(bot))
