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
        self.level_channel_id = int(config("guild_ids")['get_level_channel'])
        self.arcane_id = int(config("guild_ids")['arcane'])

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        '''Get level from message sent by Arcane bot on #level-channel'''

        try:
            if message.channel.id != self.level_channel_id:
                return

            if message.author.id != self.arcane_id:
                return

            logger.debug("Arcane on_message")

            msg = (await message.channel.history(limit=1).flatten())[0].content
            i = msg.find("has reached level ")
            if i == -1:
                return

            logger.debug(f"Arcane's message: \"{msg}\"")

            msg = msg[i + len("has reached level "):]

            level = int(msg[:msg.find(". GG!")].replace("*", ""))
            member_id = message.mentions[0].id
            username = self.bot.get_user(member_id).name

            logger.debug(f"member {username} ({member_id}) level: {level}")

            guild = self.bot.get_guild(int(config("guild_ids")['guild']))
            member = guild.get_member(member_id)

            if level >= int(config('guild_ids')['no_newbie_level']):
                await member.remove_roles(discord.Object(int(config("guild_ids")['newbie'])))

            conn = None
            try:
                db_params = config(section="postgresql")
                conn = psycopg2.connect(**db_params)
                cur = conn.cursor()

                cur.execute("select level from member where member_id=%s", (member_id,))
                row = cur.fetchone()

                if row is None:
                    cur.execute("insert into member (member_id, username, level) values(%s,%s,%s)", (
                        member_id, username, level))
                else:
                    if level > row[0]:
                        cur.execute(
                            "update member set last_update=now(), level=%s where member_id=%s", (level, member_id,))

                logger.info(
                    f"Collected level {level} from user {username} ({member_id})")
                conn.commit()
                cur.close()

            except (Exception, psycopg2.DatabaseError) as error:
                logger.exception(error)
            finally:
                if conn is not None:
                    conn.close()
        except Exception as error:
            logger.exception(error)

    @tasks.loop(seconds=12.0)
    async def process_levels(self, ctx):
        res = await process_level_static(self.bot)
        if res == True:
            await ctx.send("process_levels: Canceled")
            logger.info("process_levels Canceled")
            self.process_levels.cancel()

    @commands.command()
    async def start_levels_processing(self, ctx):
        await ctx.send("process_levels: Starting")
        logger.info("process_levels: Starting")
        self.process_levels.start(ctx)

    @commands.command()
    async def stop_levels_processing(self, ctx):
        await ctx.send("process_levels: Stopped")
        logger.info("process_levels: Stopped")
        self.process_levels.cancel()


def setup(bot):
    bot.add_cog(Levels(bot))


async def process_level_static(bot) -> bool:
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
                logger.info(
                    f"Updated ({member_id}) {username}'s level ({level})")
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
    if level >= 100:
        return guild.get_role(int(params['lvl100']))
    if level >= 90:
        return guild.get_role(int(params['lvl90']))
    if level >= 80:
        return guild.get_role(int(params['lvl80']))
    if level >= 70:
        return guild.get_role(int(params['lvl70']))
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
