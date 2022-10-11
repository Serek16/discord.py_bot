
import discord
from logger import get_logger
from discord.ext import commands
import psycopg2
import sys
from utils.bot_utils import has_role, get_global, get_id_guild, get_main_guild_id, get_postgres_credentials
from selfbot.selfbot_utils import fetchMembersLevel
from selfbot.discum_bot import DiscumBot

logger = get_logger(__name__, __name__)


class SyncDatabase(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role('staff')
    async def sync_database(self, ctx: commands.Context, sync_levels=False):
        '''synchronize the presence of members on the server and in the database'''

        await ctx.send("sync_database: Starting")
        logger.info("sync_database: Starting")

        guild = ctx.guild
        guild_members = list(guild.members)

        booster_role_id = get_id_guild('booster', guild.id)
        newbie_role_id = get_id_guild('newbie', guild.id)
        no_newbie_level = get_global('newbie_level')

        discum_bot = DiscumBot(get_global("selfbot_token"))

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

                        if sync_levels == True:
                            level = fetchMembersLevel(member, discum_bot)
                            cur2.execute(
                                'update member set level=%s, last_update=now(), member_left=false where member_id=%s', (level, db_member_id))
                        else:
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
                
                if sync_levels == True:
                    level = fetchMembersLevel(member, discum_bot)
                else:
                    level = 0

                if has_role(member, 'booster_id') == False and member.bot == False:
                    await member.add_roles(discord.Object(newbie_role_id))
                cur.execute(
                    "insert into member (member_id, username, level) values (%s, %s, %s)", (member.id, member.name, level))
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


async def setup(bot):
    await bot.add_cog(SyncDatabase(bot))
