from dis import dis
from logger import get_logger
import discord
from discord.ext import commands
import sys
from config import config

sys.path.append('../')


logger = get_logger(__name__, __name__)


class Moderation(commands.Cog):

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        '''When member is banned from one of the bot's servers, 
            automatically gets banned on any server where the bot has ban permissions'''
            
        try:
            banned = await member.guild.fetch_ban(member)
        except discord.NotFound:
            banned = False

        if banned:
            # Get a ban reason
            ban_entries = await member.guild.bans()
            for ban_entry in ban_entries:
                if ban_entry.user.id == member.id:
                    reason = ban_entry.reason
                    break
            
            logger.info(f"{member.name} ({member.id}) has been banned in {member.guild.name} ({member.guild.id}). Reason: {reason}")

            # Ban a member in every guild that bot is in and delete messages for the last 7 days
            for guild in self.bot.guilds:
                guild:discord.Guild
                try:
                    await guild.ban(member, reason=reason + f" (banned in {guild.name} [{guild.id}])" if guild.id != member.guild.id else "", delete_message_days=7)
                except discord.HTTPException as err:
                    logger.error(err)

def setup(bot):
    bot.add_cog(Moderation(bot))
