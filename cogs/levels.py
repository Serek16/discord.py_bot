import time
import discord
from logger import get_logger
from config import config
import sys
from discord.ext import commands, tasks
import psycopg2
import threading
from discum.utils.slash import SlashCommander

sys.path.append('../')

logger = get_logger(__name__, __name__)

lvl60 = 964263958271918160
lvl50 = 964252594212077718
lvl40 = 964252569012691005
lvl30 = 964252537169522748
lvl20 = 964252503522832395
lvl15 = 964252480949067826
lvl10 = 964252447763759194
lvl5 = 964250887457505320
lvl1 = 964250842746220594

selfbot = None


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=12.0)
    async def process_levels(self):
        if await process_level_static() == 0:
            self.process_levels.cancel()

    @commands.command()
    async def start_levels_processing(self, ctx):
        await ctx.send("Starting")
        self_bot_thread = threading.Thread(target=init_selfbot)
        while selfbot is not None:
            pass
        self_bot_thread.start()
        self.process_levels.start()

    @commands.command()
    async def stop_levels_processing(self, ctx):
        await ctx.send("Stopped")
        self.process_levels.cancel()


def setup(bot):
    bot.add_cog(Levels(bot))


def init_selfbot():
    import discum
    global selfbot
    selfbot = discum.Client(
        token=config(section="bot_tokens")['selfbot'], log=False)
    if selfbot is None:
        logger.error("Couldn't connect to selfbot")
    selfbot.gateway.run()


async def process_level_static(bot):
    conn = None
    try:
        params = config(section="postgresql")
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(
            "select member_id, username, level from member where member_left=false and new_server_level_given=false order by level desc LIMIT 1")

        row = cur.fetchone()
        if row is None:
            logger.info("process_levels: Stopped")
            return 0

        else:
            logger.debug(row)
            member_id = int(row[0])
            username = row[1]
            level = int(row[2])

            guild = bot.get_guild(964219276145852527)

            if level == 0:
                cur.execute(
                    'update member set last_update=now(), new_server_level_given=true where member_id=%s', (member_id,))
                conn.commit()
                conn.close()
                logger.info(
                    f"Updated ({member_id}) {username}'s level ({level})")
                return 1

            try:
                member = await guild.fetch_member(member_id)
            except (discord.Forbidden, discord.HTTPException) as memberNotFound:
                cur.execute(
                    'update member set last_update=now(), member_left=true where member_id=%s', (member_id,))
                conn.commit()
                conn.close()
                logger.info(
                    f"Updated ({member_id}) {username}'s level ({level})")
                return 1

            await member.add_roles(get_role(level, guild))

            slashCmds = selfbot.getSlashCommands(
                "437808476106784770").json()
            # slashCmds can be either a list of cmds or just 1 cmd. Each cmd is of type dict.
            s = SlashCommander(slashCmds)
            print(f"({member_id}) {username} {level}")

            data = s.get(['setlevel', ], {
                'member': member_id, 'level': level})
            selfbot.triggerSlashCommand(
                "437808476106784770", "964270265079058442", guildID="964219276145852527", data=data)

            # give time Arcane to process command and give send reponse
            time.sleep(1)

            arcane_res = (await guild.get_channel(964270265079058442).history(limit=1).flatten())[0]

            print(arcane_res.content)
            if arcane_res.content.startswith("Set"):
                logger.info(
                    f"Updated ({member_id}) {username}'s level ({level})")
                cur.execute(
                    'update member set last_update=now(), new_server_level_given=true where member_id=%s', (member_id,))
                conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        return 1


def get_role(self, level, guild):
    if level >= 60:
        return guild.get_role(lvl60)
    elif level >= 50:
        return guild.get_role(lvl50)
    elif level >= 40:
        return guild.get_role(lvl40)
    elif level >= 30:
        return guild.get_role(lvl30)
    elif level >= 20:
        return guild.get_role(lvl20)
    elif level >= 15:
        return guild.get_role(lvl15)
    elif level >= 10:
        return guild.get_role(lvl10)
    elif level >= 5:
        return guild.get_role(lvl5)
    elif level >= 1:
        return guild.get_role(lvl1)
    else:
        return guild.get_role(964230940706607164)  # member role
