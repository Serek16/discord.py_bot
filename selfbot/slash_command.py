class SlashCommand:
    def __init__(self, guild_id: int, channel_id: int, bot_id: int, command_name: str, command_args: dict = None):
        if command_args is None:
            command_args = dict()

        self.guild_id = guild_id
        self.channel_id = channel_id
        self.bot_id = bot_id
        self.command_name = command_name
        self.command_args = command_args
