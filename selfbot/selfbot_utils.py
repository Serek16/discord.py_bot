import discord
import pytesseract
from time import sleep

from selfbot.discum_bot import DiscumBot
from selfbot.slash_command import SlashCommand
from utils.bot_utils import get_id_guild, get_global


def fetchMembersLevel(member: discord.Member, discum_bot: DiscumBot):
    guild_id = member.guild.id
    channel_id = get_id_guild('set_level_channel_guild', guild_id)
    arcane_id = get_global('arcane_id')
    command_name = 'level'
    command_args = {'member': member.id}

    while True:
        discum_bot.sendSlashCommand(SlashCommand(guild_id, channel_id, arcane_id, command_name, command_args))
        sleep(100)
        guild = discum_bot.client.get_guild(guild_id)
        msg = guild.get_channel(channel_id).history(limit=1).flatten()[0]
        
        if msg.author != get_global('arcane_id'):
            continue
        else:
            print(msg)
            print(type(msg))
            # level = pytesseract.image_to_string()
            
            # return level
            continue

