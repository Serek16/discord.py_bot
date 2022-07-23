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

            user = discord.Object(member.id)
            
            # Ban a member in every guild that bot is in and delete messages for the last 7 days
            for guild in self.bot.guilds:
                guild:discord.Guild
                try:                
                    if guild.id == member.guild.id:
                        await guild.ban(user, reason=reason, delete_message_days=7)
                    else:
                        await guild.ban(user, reason=f"{reason} (banned in {member.guild.name} [{member.guild.id}])", delete_message_days=7)

                except discord.HTTPException as err:
                    logger.error(err)

    @commands.command()
    @commands.has_role(int(config("guild_ids")['admin']))
    async def ban(self, ctx, *args):
        
        if args[0] == None or args[0] == "":
            await ctx.send("Error: arg is empty")
            return

        # Parse arg[0] into an id
        try:
            if args[0].startswith("<@"):
                id = int(args[0][:2][:-1])
            else:
                id = int(args[0])

        except ValueError:
            await ctx.send("Error: arg is not a number")
            return

        user = discord.Object(id)

        # Ban a member in every guild that bot is in and delete messages for the last 7 days
        for guild in self.bot.guilds:
            guild:discord.Guild
            try:
                if guild.id == ctx.guild.id:
                    await guild.ban(user, reason=' '.join(args[1:]), delete_message_days=7)
                else:
                    await guild.ban(user, reason=f"{' '.join(args[1:])} (banned in {ctx.guild.name} [{ctx.guild.id}])", delete_message_days=7)

                logger.debug(f"User {user.name} banned in {guild.name} ({guild.id})")

            except discord.HTTPException as err:
                logger.error(err)


    @commands.command()
    @commands.has_role(int(config("guild_ids")['staff']))
    async def ban(self, ctx, *args):
        
        if args[0] == None or args[0] == "":
            await ctx.send("Error: arg is empty")
            return

        # Parse arg[0] into an id
        try:
            if args[0].startswith("<@"):
                id = int(args[0][:2][:-1])
            else:
                id = int(args[0])

        except ValueError:
            await ctx.send("Error: arg is not a number")
            return

        user = discord.Object(id)

        # Ban a member in every guild that bot is in and delete messages for the last 7 days
        for guild in self.bot.guilds:
            guild:discord.Guild
            try:
                if guild.id == ctx.guild.id:
                    await guild.ban(user, reason=' '.join(args[1:]), delete_message_days=7)
                else:
                    await guild.ban(user, reason=" ".join(args[1:]) + f" (banned in {ctx.guild.name} [{ctx.guild.id}])", delete_message_days=7)
                
                logger.debug(f"User {user.name} banned in {guild.name} ({guild.id})")

            except discord.HTTPException as err:
                logger.error(err)


def setup(bot):
    bot.add_cog(Moderation(bot))
