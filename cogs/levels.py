import time
import discord
from main import get_self_bot
from logger import get_logger
from config import config
import sys
from discord.ext import commands, tasks
import psycopg2
from discum.utils.slash import SlashCommander

sys.path.append('../')

logger = get_logger(__name__, __name__)

selfbot = None


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=12.0)
    async def process_levels(self):
        res = await process_level_static(self.bot)
        if res == True:
            logger.info("process_levels canceled")
            self.process_levels.cancel()

    @commands.command()
    async def start_levels_processing(self, ctx):
        await ctx.send("Starting")
        logger.info("start_levels_processing: Start")
        self.process_levels.start()

    @commands.command()
    async def stop_levels_processing(self, ctx):
        await ctx.send("Stopped")
        self.process_levels.cancel()


def setup(bot):
    bot.add_cog(Levels(bot))


async def process_level_static(bot) -> bool :
    ''' 
        Update member level on server using level stored in database
            Returns:
                True (bool) -> processing is done (there is nothing to update)\n
                False (bool) -> processing has more work to do
    '''
    logger.info("process_level_static iter")

    conn = None
    try:
        db_params = config(section="postgresql")
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        cur.execute(
            "select member_id, username, level from member where member_left=false and new_server_level_given=false order by level desc LIMIT 1")

        # If there is nothing to do then exit the function
        row = cur.fetchone()
        if row is None:
            return True

        else:
            member_id = row[0]
            username = row[1]
            level = row[2]

            logger.info(f"({member_id}) {username} {level}")

            params = config(section="guild_ids")
            guild = bot.get_guild(int(params['guild']))

            if level == 0:
                cur.execute(
                    'update member set last_update=now(), new_server_level_given=true where member_id=%s', (member_id,))
                conn.commit()
                cur.close()
                conn.close()
                logger.info(f"Updated ({member_id}) {username}'s level ({level})")
                return False

            try:
                member = await guild.fetch_member(member_id)
            except (discord.Forbidden, discord.HTTPException) as memberNotFound:
                cur.execute(
                    'update member set last_update=now(), member_left=true where member_id=%s', (member_id,))
                conn.commit()
                cur.close()
                conn.close()
                logger.info(
                    f"Updated ({member_id}) {username}'s level ({level})")
                return False

            await member.add_roles(get_role(level, guild, params))

            selfbot = get_self_bot()
            ### discum selfbot code ###
            slashCmds = selfbot.getSlashCommands(str(params['arcane'])).json()
            # slashCmds can be either a list of cmds or just 1 cmd. Each cmd is of type dict.
            s = SlashCommander(slashCmds)
            data = s.get(['setlevel', ], {
                'member': member_id, 'level': level})

            selfbot.triggerSlashCommand(
                str(params['arcane']), str(params['level_channel']), guildID=str(params['guild']), data=data)
            ### ###

            # give time Arcane to process command and give send reponse
            time.sleep(1)

            arcane_res = (await guild.get_channel(int(params['level_channel'])).history(limit=1).flatten())[0]

            if arcane_res.content.startswith("Set"):
                logger.info(
                    f"Updated ({member_id}) {username}'s level ({level})")
                cur.execute(
                    'update member set last_update=now(), new_server_level_given=true where member_id=%s', (member_id,))
                conn.commit()

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    
    return False


def get_role(level, guild, params):
    if level >= 60:
        return guild.get_role(int(params['lvl60']))
    elif level >= 50:
        return guild.get_role(int(params['lvl50']))
    elif level >= 40:
        return guild.get_role(int(params['lvl40']))
    elif level >= 30:
        return guild.get_role(int(params['lvl30']))
    elif level >= 20:
        return guild.get_role(int(params['lvl20']))
    elif level >= 15:
        return guild.get_role(int(params['lvl15']))
    elif level >= 10:
        return guild.get_role(int(params['lvl10']))
    elif level >= 5:
        return guild.get_role(int(params['lvl5']))
    elif level >= 1:
        return guild.get_role(int(params['lvl1']))
    else:
        return guild.get_role(int(params['member']))
