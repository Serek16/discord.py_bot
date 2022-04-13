from multiprocessing import get_logger
from discord.ext import commands
import psycopg2

from config import config


logger = get_logger(__name__, __name__)


class Invite(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def database(self, ctx):
        old_guild_id = 820938383295119361
        new_guild_id = 910458854985318430

        old_guild_role_id = 932060695569256448

        old_guild = await self.fetch_guild(old_guild_id)
        new_guild = await self.fetch_guild(new_guild_id)

        conn = None
        try:
            params = config(section="postgresql")
            params['database'] = 'old_member'
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            
            for member in old_guild.members:
                logger.debug(f"{member.name} ({member.id}) added to the database")
                cur.execute("insert into old_member () values (%s,)")                   
        
            
            
            conn.commit()
            cur.close()


        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            conn.close()

        logger.info("done")
        await ctx.send("done")

def setup(bot):
    bot.add_cog(Invite(bot))

