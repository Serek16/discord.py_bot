from dis import disco
from hashlib import new
import discord
from logger import get_logger
from config import config
from discord.ext import commands
import psycopg2
import sys

sys.path.append('../')



logger = get_logger(__name__)


class NewMember(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''Add each member that joins the server to the database'''

        logger.info(f"Member ({member.name}, {member.id}) joined the server")
        newbie = True
        conn = None
        try:
            params = config(section="postgresql")
            conn = psycopg2.connect(**params)

            cur = conn.cursor()
            cur.execute(
                "select level from member where member_id=%s", (member.id,))

            # member doesn't exist in the databse
            row = cur.fetchone()
            if row is None:
                logger.debug("^ no record in the database")
                cur.execute(
                    "insert into member (member_id, username) values (%s, %s)", (member.id, member.name))

            # member do exist in the database
            else:
                logger.debug("^ already exists in the database")
                cur.execute(
                    "update member set last_join=now(), last_update=now(), member_left=false where member_id=%s", (member.id,))

                if row[0] >= 3:
                    newbie = False

            if newbie == True:
                await member.add_roles(self.bot.get_guild(964219276145852527).get_role(964257860475293709))

            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(f"member.id {member.id}")
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        '''Update the databse when a member leave the server'''

        logger.info(f"Member ({member.name}, {member.id}) left the server")
        conn = None
        try:
            params = config(section="postgresql")
            conn = psycopg2.connect(**params)

            cur = conn.cursor()
            cur.execute(
                "select * from member where member_id=%s", (member.id,))

            # member doesn't exist in databse
            if cur.fetchone() is None:
                cur.execute(
                    "insert into member (member_id, username, member_left) values (%s, %s, true)", (member.id, member.name))

            # member do exist in database
            else:
                cur.execute(
                    "update member set last_update=now(), member_left=true where member_id=%s", (member.id,))

            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(f"member.id {member.id}")
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()

    @commands.command()
    async def sync_database(self, ctx):
        '''synchronize the presence of members on the server and in the database'''
        await ctx.send("update_database: Starting")
        logger.info("update_database: Done")

        conn = None
        try:
            params = config(section="postgresql")
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur2 = conn.cursor()

            cur.execute("select member_id, username, member_left from member")
            row = cur.fetchone()

            guild = await self.bot.fetch_guild(964219276145852527)
            while row is not None:
                member_id = row[0]
                username = row[1]
                member_left = row[2]

                try:
                    print('try')
                    member = await guild.fetch_member(member_id)
                    print(f"({member.id}) {member.name} {member_left}")
                    if member_left == True:
                        cur2.execute(
                            'update member set last_update=now(), member_left=false where member_id=%s', (member_id,))
                        logger.info(
                            f"Updated member ({member_id}) {username} member_left=false")
                    
                except (discord.Forbidden, discord.HTTPException) as error:
                    if member_left == False:
                        cur2.execute(
                            'update member set last_update=now(), member_left=true where member_id=%s', (member_id,))
                        logger.info(
                            f"Updated member ({member_id}) {username} member_left=true")

                conn.commit()
                row = cur.fetchone()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print("update_database: Canceled")
            logger.error(error)
        finally:
            if conn is not None:
                conn.close()
            logger.info("update_database: Done")
            await ctx.send("update_database: Done")


def setup(bot):
    bot.add_cog(NewMember(bot))
