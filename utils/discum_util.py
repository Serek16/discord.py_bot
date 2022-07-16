import discord
from time import sleep
from config import config
import main
# import pytesseract
import discum

def fetchMembersLevel(member_id: int, bot: discord.Client):
    selfbot = main.getSelfBot()
    
    params = config(section="guild_ids")

    slashCmds = selfbot.getSlashCommands(str(params['arcane'])).json()
    # slashCmds can be either a list of cmds or just 1 cmd. Each cmd is of type dict.
    s = SlashCommander(slashCmds)
    data = s.get(['level', ], {'member': member_id})


    while True:
        # Use slash command in a specified text channel
        selfbot.triggerSlashCommand(
            str(params['arcane']), str(params['level_channel']), guildID=str(params['guild']), data=data)
    
        sleep(100)
        guild = bot.get_guild((int(config(section="guild_ids")['guild'])))
        msg = guild.get_channel(int(params['level_channel'])).history(limit=1).flatten()[0]
        
        if msg.author != int(params['arcane']):
            continue
        else:
            print(msg)
            print(type(msg))
            # level = pytesseract.image_to_string()
            return level


