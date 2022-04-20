import discord
from cogs.levels import process_level_static
from logger import get_logger
from config import config
from discord.ext import commands, tasks
import psycopg2
import sys

sys.path.append('../')

logger = get_logger(__name__, __name__)


class NewMember(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.level_processing = False

    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''Add each member that joins the server to the database'''

        if member.guild.id != int(config(section="guild_ids")['guild']):
            return

        logger.info(f"Member ({member.name}, {member.id}) joined the server")
        
        newbie = True
        conn = None
        try:
            db_params = config(section="postgresql")
            conn = psycopg2.connect(**db_params)

            cur = conn.cursor()
            cur.execute(
                "select level from member where member_id=%s", (member.id,))

            row = cur.fetchone()

            # member doesn't exist in the databse
            if row is None:
                logger.info(f"{member.name}: no record in the database")
                cur.execute(
                    "insert into member (member_id, username) values (%s, %s)", (member.id, member.name))

            # member exists in the database
            else:
                logger.info(f"{member.name}: already exists in the database")
                cur.execute(
                    "update member set last_join=now(), last_update=now(), member_left=false where member_id=%s", (member.id,))

                if row[0] >= 3:
                    newbie = False
                
                if self.level_processing == False and row[0] >= 1:
                    self.level_processing = True
                    logger.info("on_member_join: Started level processing")
                    self.process_levels.start()

            params = config(section="guild_ids")
            if newbie == True and member.bot == False:
                await member.add_roles(self.bot.get_guild(int(params['guild'])).get_role(int(params['newbie'])))

            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(f"member.id {member.id}")
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()


    @tasks.loop(seconds=12.0)
    async def process_levels(self):
        if await process_level_static(self.bot) == True:
            self.process_levels.cancel()
            self.level_processing = False            
            
            logger.info("process_levels: Canceled")


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        '''Update the databse when a member leave the server'''

        if member.guild.id != int(config(section="guild_ids")['guild']):
            return

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
                logger.info(f"{member.name}: no record in the database")
                cur.execute(
                    "insert into member (member_id, username, new_server_level_given, member_left) values (%s, %s, true, true)", (member.id, member.name))

            # member exists in database
            else:
                logger.info(f"{member.name}: already exists in the database")
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

        await ctx.send("sync_database: Starting")
        logger.info("sync_database: Starting")

        guild = await self.bot.fetch_guild(int(config(section="guild_ids")['guild']))
        members = guild.members

        conn = None
        try:
            db_params = config(section="postgresql")
            conn = psycopg2.connect(**db_params)
            cur = conn.cursor()
            cur2 = conn.cursor()

            cur.execute("select count(*) from member")
            total_member_num = cur.fetchone()[0]
            i = 1

            cur.execute("select member_id, username, member_left from member")
            row = cur.fetchone()

            while row is not None:
                member_id = row[0]
                username = row[1]
                member_left = row[2]
                
                logger.info(f"Checking: ({member_id}) {username} {member_left} [{i}/{total_member_num}]")
                
                found = False
                for member in members:
                    if member.id == member_id:
                        found = True
                    members.remove(member)
                
                if found == True:
                    if member_left == True:
                        cur2.execute(
                            'update member set last_update=now(), member_left=false where member_id=%s', (member_id,))
                        logger.info(
                            f"Updated member ({member_id}) {username} member_left=false")
                
                else:
                    if member_left == False:
                        cur2.execute(
                            'update member set last_update=now(), member_left=true where member_id=%s', (member_id,))
                        logger.info(
                            f"Updated member ({member_id}) {username} member_left=true")

                conn.commit()
                row = cur.fetchone()
                i += 1
            
            for i, member in enumerate(members):
                logger.info(f"Member ({member.id}) {member.name} not in the database [{i}/{len(members)}]")
                cur.execute("insert into member (member_id, username) values (%s, %s)", (member.id, member.name))

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


def setup(bot):
    bot.add_cog(NewMember(bot))
