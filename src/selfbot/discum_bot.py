from discum.utils.slash import SlashCommander
import discum

from threading import Thread
from src.selfbot.slash_command import SlashCommand


class DiscumBot:
    def __init__(self, token: str, log=False):
        self.client = discum.Client(token=token, log=log)
        thread = Thread(target=self.run_client_in_thread)
        thread.start()

    def run_client_in_thread(self):
        self.client.gateway.run()

    def __triggerSlashCommand(self, resp, guild_id: int, channel_id: int, bot_id: int, command_name: str,
                              command_args: dict):
        if resp.event.ready_supplemental:
            self.client.gateway.request.searchSlashCommands(str(guild_id), limit=10, query=command_name)
        if resp.event.guild_application_commands_updated:
            self.client.gateway.removeCommand(self.__triggerSlashCommand)
            slash_cmds = resp.parsed.auto()['application_commands']
            s = SlashCommander(slash_cmds, application_id=str(bot_id))
            data = s.get([command_name], inputs=command_args)
            self.client.triggerSlashCommand(str(bot_id), channelID=str(channel_id), guildID=str(guild_id), data=data,
                                            sessionID=self.client.gateway.session_id)

    def sendSlashCommand(self, slash_command: SlashCommand):
        guild_id = slash_command.guild_id
        channel_id = slash_command.channel_id
        bot_id = slash_command.bot_id
        command_name = slash_command.command_name
        command_args = slash_command.command_args

        slash_cmds = self.client.getSlashCommands(str(bot_id)).json()
        s = SlashCommander(slash_cmds)
        data = s.get([command_name], inputs=command_args)
        self.client.triggerSlashCommand(bot_id, channelID=channel_id, guildID=guild_id, data=data)
