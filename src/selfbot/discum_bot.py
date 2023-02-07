from discum.utils.slash import SlashCommander
import discum

from threading import Thread
from src.selfbot.slash_command import SlashCommand


class DiscumBot:
    def __init__(self, token: str, log=False):
        self.client = discum.Client(token=token, log=log)
        self.__thread = Thread(target=self.__run_client_in_thread)
        self.__thread.start()

    def __del__(self):
        self.client.gateway.close()
        self.__thread.join()

    def __run_client_in_thread(self):
        self.client.gateway.run()

    def send_slash_command(self, slash_command: SlashCommand):
        guild_id = slash_command.guild_id
        channel_id = slash_command.channel_id
        bot_id = slash_command.bot_id
        command_name = slash_command.command_name
        command_args = slash_command.command_args

        slash_cmds = self.client.getSlashCommands(str(bot_id)).json()
        s = SlashCommander(slash_cmds)
        data = s.get([command_name], inputs=command_args)
        self.client.triggerSlashCommand(bot_id, channelID=channel_id, guildID=guild_id, data=data)
