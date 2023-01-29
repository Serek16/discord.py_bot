import discord
from discord import Object
from discord.ext import commands

from src.model.member import Member
from src.utils.bot_utils import has_role
from src.utils.config_val_io import AggregatedGuildValues, GlobalValues, GuildSpecificValues
from src.utils.databaseIO import get_member_by_id, save_member
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


class Levels(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        """Get level from message sent by Arcane bot on #level-channel."""

        # Continue if it's a message sent by Arcane in a specific level channel.
        if message.channel.id not in [tup[1] for tup in AggregatedGuildValues.get('get_levels_channel_id')] \
                or message.author.id != GlobalValues.get('arcane_id'):
            return

        # It has to be specific message sent by Arcane "@username has reached level [level]. GG!".
        result = await self.__read_message(message)
        if result is None:
            return

        username, member_id, level = result

        logger.debug(f"member {username} ({member_id}) level: {level}.")

        guild = message.guild
        member = guild.get_member(member_id)

        # If level is greater than or equals no_newbie_level, member is no longer a newbie.
        if level >= GlobalValues.get('newbie_level'):
            if has_role(member, GuildSpecificValues.get(guild.id, 'newbie')):
                await member.remove_roles(Object(GuildSpecificValues.get(guild.id, 'newbie')))
                logger.debug(f"User {member.name} is no longer a newbie.")

        db_member = get_member_by_id(member_id)
        if db_member is None:
            save_member(Member(member_id, username, level))
        else:
            if level > db_member.level:
                db_member.level = level
                save_member(db_member)

        logger.info(
            f"Collected level {level} from user {username}#{member.discriminator} ({member_id}).")

    async def __read_message(self, message: discord.Message) -> tuple[str, int, int] | None:
        """Extract username, member_id and level from Arcanes message.
        The message need to have "@username has reached level **[level]**. GG!" structure."""

        msg = [msg async for msg in message.channel.history(limit=1)][0].content
        i = msg.find("has reached level ")

        # The phrase wasn't found
        if i == -1:
            return None

        # Process the level message from Arcane. Extract level, username and member_id
        msg = msg[i + len("has reached level "):]
        level = int(msg[:msg.find(". GG!")].replace("*", ""))
        member_id = message.mentions[0].id
        username = self.bot.get_user(member_id).name

        return username, member_id, level


async def setup(bot):
    await bot.add_cog(Levels(bot))
