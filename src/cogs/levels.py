import discord
from src.utils.logger import get_logger
from discord.ext import commands
import psycopg2

from src.utils.bot_utils import get_global, get_id_guild, get_ids, get_postgres_credentials

logger = get_logger(__name__, __name__)


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        """Get level from message sent by Arcane bot on #level-channel"""

        # Continue if it's a message sent by Arcane in a specific level channel
        if message.channel.id not in get_ids('get_levels_channel_id') or message.author.id != get_global('arcane_id'):
            return

        try:
            logger.debug("Arcane on_message")

            # It has to be specific message sent by Arcane "@username has reached level <level> ..."
            msg = ((await message.channel.history(limit=1)).flatten())[0].content
            i = msg.find("has reached level ")
            if i == -1:
                return

            logger.debug(f"Arcane's message: \"{msg}\"")

            # Process message, extract the level, username and member_id
            msg = msg[i + len("has reached level "):]
            level = int(msg[:msg.find(". GG!")].replace("*", ""))
            member_id = message.mentions[0].id
            username = self.bot.get_user(member_id).name

            logger.debug(f"member {username} ({member_id}) level: {level}")

            guild: discord.Guild = message.guild
            member = guild.get_member(member_id)

            # If level is greater than or equals no_newbie_level, member is no longer a newbie
            if level >= get_global('newbie_level'):
                await member.remove_roles(guild.get_role(get_id_guild('newbie', guild.id)))
                logger.debug(f"User {member.name} is no longer a newbie")

            conn = None
            try:
                db_params = get_postgres_credentials()
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


async def setup(bot):
    await bot.add_cog(Levels(bot))
