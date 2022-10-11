import discord
from logger import get_logger
from discord.ext import commands
import psycopg2

from utils.bot_utils import get_global, get_id_guild, get_main_guild_id, get_postgres_credentials

logger = get_logger(__name__, __name__)


class NewMember(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Add each member that joins the server to the database"""

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

            # Member doesn't exist in the database
            if row is None:
                logger.info(f"{member.name}: no record in the database")
                cur.execute(
                    "insert into member (member_id, username) values (%s, %s)", (member.id, member.name))

            # Member exists in the database
            else:
                logger.info(f"{member.name}: already exists in the database")
                cur.execute(
                    "update member set last_join=now(), last_update=now(), member_left=false where member_id=%s",
                    (member.id,))

                # If level is greater than or equals minimal required level to not be a newbie anymore
                if row[0] >= get_global('newbie_level'):
                    newbie = False

            guild = member.guild
            if newbie is True and member.bot is False:
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
        """Update the database when a member leave the server"""

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

            # Member doesn't exist in the database
            if cur.fetchone() is None:
                logger.info(f"{member.name}: no record in the database")
                cur.execute(
                    "insert into member (member_id, username, member_left) values (%s, %s, true)",
                    (member.id, member.name))

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


async def setup(bot):
    await bot.add_cog(NewMember(bot))
