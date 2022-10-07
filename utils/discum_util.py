import discord
from time import sleep
import main
import discum

from utils.bot_utils import get_global, get_id_guild, get_main_guild_id

def fetchMembersLevel(member_id: int, bot: discord.Client):
    raise NotImplementedError("fetchMembersLevel function isn't implemented correctly yet")
    
    selfbot = main.getSelfBot()

    slashCmds = selfbot.getSlashCommands(get_global('selfbot_token')).json()
    # slashCmds can be either a list of cmds or just 1 cmd. Each cmd is of type dict.
    s = SlashCommander(slashCmds)
    data = s.get(['level', ], {'member': member_id})

    guild_id = None # TODO guild id is required. Tip: add an argument to the current function

    while True:
        # Use slash command in a specified text channel
        selfbot.triggerSlashCommand(
            str(get_global('arcane_id')), str(get_id_guild(guild_id, 'set_level_channel_guild')), guildID=str(guild_id), data=data)
    
        sleep(100)
        guild_id = get_main_guild_id()
        guild = bot.get_guild(guild_id)
        msg = guild.get_channel(get_id_guild(guild_id, 'set_level_channel_id')).history(limit=1).flatten()[0]
        
        if msg.author != get_global('arcane_id'):
            continue
        else:
            print(msg)
            print(type(msg))
            # level = pytesseract.image_to_string()
            # return level
