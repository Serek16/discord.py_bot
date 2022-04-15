from discord.ext import commands
import psycopg2
import sys  

sys.path.append('../')
from config import config
from logger import get_logger


logger = get_logger(__name__)


class NewMember(commands.Cog):
        
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''Add each member that joins the server to the database'''
        
        logger.info(f"Member ({member.name}, {member.id}) joined the server")
        conn = None
        try:
            params = config(section="postgresql")
            conn = psycopg2.connect(**params)

            cur = conn.cursor()
            cur.execute("select * from member where member_id=%s", (member.id,))
            
            # member doesn't exist in the databse
            if cur.fetchone() is None:
                logger.debug("^ no record in the database")
                cur.execute("insert into member (member_id, username) values (%s, %s)", (member.id, member.name))
            
            # member do exist in the database
            else:
                logger.debug("^ already exists in the database")
                cur.execute("update member set last_join=now(), last_update=now(), member_left=false where member_id=%s", (member.id,))
            
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
            cur.execute("select * from member where member_id=%s", (member.id,))

            # member doesn't exist in databse
            if cur.fetchone() is None:
                cur.execute("insert into member (member_id, username, member_left) values (%s, %s, true)", (member.id, member.name))
            
            # member do exist in database
            else:
                cur.execute("update member set last_update=now(), member_left=true where member_id=%s", (member.id,))
            
            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(f"member.id {member.id}")
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()


def setup(bot):
    bot.add_cog(NewMember(bot))