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
        conn = None
        try:
            logger.info("Member joined the server")
            params = config(section="postgresql")
            conn = psycopg2.connect(**params)

            cur = conn.cursor()
            cur.execute("select * from member where member_id=%s", (member.id,))
            
            # member doesn't exist in databse
            if cur.fetchone() == None:
                logger.debug("- no record in a the database")
                cur.execute("insert into member (member_id, username) values (%s, %s)", (member.id, member.name))
            
            # member do exist in database
            else:
                logger.debug("- already exists in the database")
                cur.execute("update member set last_join=now(), last_updated=now(), server_member=true where member_id=%s", (member.id,))
            
            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()


    @commands.Cog.listener()
    async def on_member_leave(self, member):
        '''Update the databse when a member leave the server'''

        conn = None
        try:
            params = config(section="postgresql")
            conn = psycopg2.connect(**params)

            cur = conn.cursor()
            cur.execute("select * from member where member_id=%s", (member.id,))

            # member doesn't exist in databse
            if cur.fetchone() == None:
                cur.execute("insert into member (member_id, username, server_member) values (%s, %s, false)", (member.id, member.name))
            
            # member do exist in database
            else:
                cur.execute("update member set last_updated=now(), server_member=false where member_id=%s", (member.id,))
            
            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()


def setup(bot):
    bot.add_cog(NewMember(bot))