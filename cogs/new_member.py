import discord
from logger import get_logger
from discord.ext import commands
import psycopg2
import sys

from utils.bot_utils import get_global, get_id_guild, get_main_guild_id, get_postgres_credentials

sys.path.append('../')

logger = get_logger(__name__, __name__)


class NewMember(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        '''Add each member that joins the server to the database'''

        # Focus only on the main server
        if member.guild.id != get_main_guild_id():
            return

        logger.info(f"Member {member.name} ({member.id}) joined the server")

        newbie = True
        conn = None
        try:
            db_params = get_postgres_credentials()
            conn = psycopg2.connect(**db_params)
            cur = conn.cursor()

            cur.execute(
                "select level from member where member_id=%s", (member.id,))
            row = cur.fetchone()

            # Member doesn't exist in the databse
            if row is None:
                logger.info(f"{member.name}: no record in the database")
                cur.execute(
                    "insert into member (member_id, username) values (%s, %s)", (member.id, member.name))

            # Member exists in the database
            else:
                logger.info(f"{member.name}: already exists in the database")
                cur.execute(
                    "update member set last_join=now(), last_update=now(), member_left=false where member_id=%s", (member.id,))

                # If level is greater than or equals 5, member is no longer a newbie
                if row[0] >= 5:
                    newbie = False

            guild = member.guild
            if newbie == True and member.bot == False:
                await member.add_roles(guild.get_role(get_id_guild('newbie', guild.id)))

            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        '''Update the databse when a member leave the server'''

        # Focus only on the main server
        if member.guild.id != get_main_guild_id():
            return

        logger.info(f"Member {member.name} ({member.id}) left the server")

        conn = None
        try:
            params = get_postgres_credentials()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            cur.execute(
                "select * from member where member_id=%s", (member.id,))

            # Member doesn't exist in the databse
            if cur.fetchone() is None:
                logger.info(f"{member.name}: no record in the database")
                cur.execute(
                    "insert into member (member_id, username, member_left) values (%s, %s, true)", (member.id, member.name))

            # Member exists in the database
            else:
                logger.info(f"{member.name}: already exists in the database")
                cur.execute(
                    "update member set last_update=now(), member_left=true where member_id=%s", (member.id,))

            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()

    @commands.command()
    @commands.has_role('staff')
    async def sync_database(self, ctx: commands.Context):
        '''synchronize the presence of members on the server and in the database'''

        await ctx.send("sync_database: Starting")
        logger.info("sync_database: Starting")

        guild = ctx.guild
        guild_members = guild.members

        booster_role_id = get_id_guild('booster', guild.id)
        newbie_role_id = get_id_guild('newbie', guild.id)
        no_newbie_level = get_global('newbie_level')

        conn = None
        try:
            db_params = get_postgres_credentials()
            conn = psycopg2.connect(**db_params)
            cur = conn.cursor()
            cur2 = conn.cursor()

            cur.execute("select count(*) from member")
            total_member_num = cur.fetchone()[0]
            i = 1

            cur.execute(
                "select member_id, username, member_left, level from member")
            row = cur.fetchone()

            while row is not None:
                db_member_id = row[0]
                db_username = row[1]
                db_member_left = row[2]
                level = row[3]

                logger.info(
                    f"Checking: ({db_member_id}) {db_username} {db_member_left} [{i}/{total_member_num}]")

                # Check if the member is still on the server
                member = None
                for _member in guild_members:
                    if _member.id == db_member_id:
                        member = _member
                        guild_members.remove(member)

                # If member is still on the server
                if member is not None:
                    if db_member_left == True:
                        cur2.execute(
                            'update member set last_update=now(), member_left=false where member_id=%s', (db_member_id,))

                    if level >= no_newbie_level:
                        if has_role(member, newbie_role_id) == True:
                            await member.remove_roles(discord.Object(newbie_role_id))
                    else:
                        # If member's level is lower than minimal level required to no longer be a newbie and he isn't a booster nor he's a bot
                        # and doesn't have newbie role already
                        if has_role(member, newbie_role_id) == False and has_role(member, booster_role_id) == False and member.bot == False:
                            await member.add_roles(discord.Object(newbie_role_id))

                # If member is no loner on the server
                else:
                    if db_member_left == False:
                        cur2.execute(
                            'update member set last_update=now(), member_left=true where member_id=%s', (db_member_id,))

                conn.commit()
                row = cur.fetchone()
                i += 1

            logger.info("Searching through members that are on the server but are not in the database")

            # Search through members that are on the server but are not in the database
            for i, member in enumerate(guild_members):
                logger.info(
                    f"Member ({member.id}) {member.name} not in the database [{i}/{len(guild_members)}]")
                # Assume that he's a newbie because level progressing level module hasn't yet saved his profile in the database
                if has_role(member, 'booster_id') == False:
                    await member.add_roles(discord.Object(newbie_role_id))
                cur.execute(
                    "insert into member (member_id, username) values (%s, %s)", (member.id, member.name))
                conn.commit()

            cur.close()

            logger.info("sync_database: Done")
            await ctx.send("sync_database: Done")

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            logger.info("sync_database: Canceled")
            await ctx.send("sync_database: Canceled")
        finally:
            if conn is not None:
                conn.close()


def has_role(member, role_id):
    for role in member.roles:
        if role.id == role_id:
            return True
    return False


def setup(bot):
    bot.add_cog(NewMember(bot))
