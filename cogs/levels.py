import discord
from logger import get_logger
from config import config
import sys
from discord.ext import commands
import psycopg2

sys.path.append('../')

logger = get_logger(__name__, __name__)


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.level_channel_id = int(config("guild_ids")['get_level_channel'])
        self.arcane_id = int(config("guild_ids")['arcane'])

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        '''Get level from message sent by Arcane bot on #level-channel'''

        # Continue if it's a message sent by Arcane in a specific level channel
        if message.channel.id != self.level_channel_id or message.author.id != self.arcane_id:
            return

        try:
            logger.debug("Arcane on_message")

            # It has to be specific message sent by Arcane "@username has reached level <level> ..."
            msg = (await message.channel.history(limit=1).flatten())[0].content
            i = msg.find("has reached level ")
            if i == -1:
                return

            logger.debug(f"Arcane's message: \"{msg}\"")

            # Process message, extract a the level, username and member_id
            msg = msg[i + len("has reached level "):]
            level = int(msg[:msg.find(". GG!")].replace("*", ""))
            member_id = message.mentions[0].id
            username = self.bot.get_user(member_id).name

            logger.debug(f"member {username} ({member_id}) level: {level}")

            guild = self.bot.get_guild(int(config("guild_ids")['guild']))
            member = guild.get_member(member_id)

            # If level is greater than or equals no_newbie_level, member is no longer a newbie
            if level >= int(config('guild_ids')['no_newbie_level']):
                await member.remove_roles(discord.Object(int(config("guild_ids")['newbie'])))
                logger.debug(f"User {member.name} is no longer a newbie")

            conn = None
            try:
                db_params = config(section="postgresql")
                conn = psycopg2.connect(**db_params)
                cur = conn.cursor()

                cur.execute(
                    "select level from member where member_id=%s", (member_id,))
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


def setup(bot):
    bot.add_cog(Levels(bot))
