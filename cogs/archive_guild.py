import discord
import traceback
from logger import get_logger
from discord.ext import commands
import psycopg2
from config import config

logger = get_logger(__name__, __name__)


class ArchiveGuild(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.archive_guild_id = int(config("guild_ids")['archive_guild'])
        self.new_guild_id = int(config("guild_ids")['guild'])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''
            Save the member who joins the archive server to the database to the "old_member" table.
            Tag him if he isn't member of the new server
        '''

        if member.guild.id != self.archive_guild_id:
            return

        logger.info(
            f"Member ({member.id}) {member.name} joined the archive server")

        new_server_member = False
        new_guild = self.bot.get_guild(self.new_guild_id)
        if new_guild.get_member(member.id) is not None:
            new_server_member = True

        conn = None
        try:
            db_params = config("postgresql")
            conn = psycopg2.connect(**db_params)
            cur = conn.cursor()

            cur.execute(
                "select * from old_member where member_id=%s", (member.id,))
            row = cur.fetchone()

            if row is not None:
                cur.execute(
                    "update old_member set last_update=now(), last_join=now(), server_member=true, new_server_member=%s where member_id=%s", (member.id, new_server_member))
            else:
                cur.execute("insert into old_member (member_id, username, new_server_member) values(%s, %s, %s)",
                            (member.id, member.name, new_server_member))

            if new_server_member == False:
                await member.add_roles(discord.Object(int(config('guild_ids')['no_new_guild_role'])))

            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        '''
            Save the member how leaves the arhive server to the database to the "old_member" table.
            Tag him if he isn't member of the new server
        '''

        if member.guild.id != self.archive_guild_id:
            return

        logger.info(
            f"Member ({member.id}) {member.name} left the archive server")

        new_server_member = False
        new_guild = self.bot.get_guild(self.new_guild_id)
        if new_guild.get_member(member.id) is not None:
            new_server_member = True

        conn = None
        try:
            db_params = config("postgresql")
            conn = psycopg2.connect(**db_params)
            cur = conn.cursor()

            cur.execute(
                "select * from old_member where member_id=%s", (member.id,))
            row = cur.fetchone()

            if row is not None:
                cur.execute(
                    "update old_member set last_update=now(), server_member=false, new_server_member=%s where member_id=%s", (new_server_member, member.id))
            else:
                cur.execute("insert into old_member (member_id, username, new_server_member) values(%s, %s, %s)",
                            (member.id, member.name, new_server_member))

            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.exception(error)
        finally:
            if conn is not None:
                conn.close()
 
    @commands.command()
    @commands.has_role(int(config("guild_ids")['staff']))
    async def database(self, ctx):
        '''Update table "old_member"'''

        old_guild = self.bot.get_guild(self.archive_guild_id)
        new_guild = self.bot.get_guild(self.new_guild_id)

        conn = None
        try:
            params = config(section="postgresql")
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur2 = conn.cursor()

            await ctx.send("Starting")

            # get number of member from the database
            cur.execute("select count(*) from old_member")
            db_member_count = cur.fetchone()
            i = 1

            members = old_guild.members

            cur2.execute("select member_id, username from old_member")
            row = cur2.fetchone()
            while row is not None:
                member_id = row[0]
                username = row[1]

                logger.info(f"Checking member ({member_id}) {username}")

                still_on_the_server = False
                for member in members:
                    if member.id == member_id:
                        still_on_the_server = True
                        members.remove(member)
                        break

                new_server_member = False
                if new_guild.get_member(member.id) is not None:
                    new_server_member = True

                logger.info(
                    f"{username} ({member_id}) updated row in the database [{i}/{db_member_count}]")
                cur.execute(
                    "update old_member set last_update=now(), server_member=%s, new_server_member=%s where member_id=%s", (still_on_the_server, new_server_member, member_id))

                # give or remove 'no new guild member'
                if still_on_the_server:
                    has_role = False    # if has the the role
                    for role in member.roles:
                        if role.id == 932060695569256448:
                            has_role = True

                    if new_server_member == False and has_role == False:
                        await member.add_roles(discord.Object(932060695569256448))

                    elif new_server_member == True and has_role == True:
                        await member.remove_roles(discord.Object(932060695569256448))

                conn.commit()
                i += 1
                row = cur2.fetchone()

            # members who are no longer on the archive server
            left_members = len(members)
            i = 0
            for member in members:

                new_server_member = False
                if new_guild.get_member(member.id) is not None:
                    new_server_member = True

                logger.info(
                    f"{member.name} ({member.id}) added to the database [{i}/{left_members}]")
                cur.execute("insert into old_member (member_id, username, new_server_member) values (%s, %s, %s)", (
                    member.id, member.name, new_server_member))

                conn.commit()
                i += 1

            cur.close()
            cur2.close()

            logger.info("done")
            await ctx.send("done")

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            logger.info("canceled")
            await ctx.send("canceled")
            print(traceback.format_exc())
        finally:
            if conn is not None:
                conn.close()


def setup(bot):
    bot.add_cog(ArchiveGuild(bot))
