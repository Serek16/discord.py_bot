import asyncio
from datetime import datetime
from threading import Thread

import selfcord

from src.model.member import Member
from src.utils.config_val_io import GlobalValues
from src.utils.databaseIO import save_member, get_all_members
from src.utils.logger import get_logger
from src.utils.singleton import SingletonMeta

logger = get_logger(__name__, __name__)


class Selfbot(metaclass=SingletonMeta):
    def __init__(self, token: str):
        self.client = self.SelfcordClient()
        self.__thread = Thread(target=self.__run_client_in_thread, args=(token,))
        self.__thread.start()

    def __run_client_in_thread(self, token: str):
        self.client.run(token)

    class SelfcordClient(selfcord.Client):
        async def on_ready(self):
            print(f'Logged in as {self.user} (ID: {self.user.id})')
            print('------')

        async def on_message(self, msg: selfcord.Message):
            if msg.content.startswith(';'):
                if msg.content[1:] == "sync_database":
                    await sync_database(self, msg)


async def sync_database(client: selfcord.Client, msg: selfcord.Message):
    """synchronize the presence of members on the server and in the database"""

    await msg.channel.send("sync_database: Starting")
    logger.info("sync_database: Starting")

    main_guild = client.get_guild(964219276145852527)
    guild = msg.guild
    guild_members = list(guild.members)

    db_member_list = get_all_members()
    db_member_count = len(db_member_list)

    for i, db_member in enumerate(db_member_list):
        logger.info(f"Checking: {db_member.username} @{db_member.member_id} [{i}/{db_member_count}]")

        member = guild.get_member(db_member.member_id)

        # If the member is still on this server, and he's still on the main server
        if main_guild.get_member(db_member.member_id) is not None and member is not None:
            logger.info(f" {member.name} is still on the server")
            db_member.member_left = False
            db_member.first_join = min(member.joined_at, db_member.first_join)

        # If member is no longer on any of the servers
        else:
            logger.info(f" {db_member.username} is no longer on the server")
            db_member.member_left = True

        # If the member has rejoined the field joined_at from Discord.Member is reseted.
        # So we check the date of member's first message sent in the server
        try:
            first_message_date = await get_first_message_date(db_member.member_id, guild.id)
            db_member.first_join = min(first_message_date, db_member.first_join)
        except KeyError as e:
            logger.error(e)

        save_member(db_member)

        # Remove member who was just examined from the list of all users in the guild.
        # List of users who remain will be later used to examine members who aren't in the databse yet
        for m in guild_members:
            if m.id == db_member.member_id:
                guild_members.remove(m)
                break

        await asyncio.sleep(0.5)

    logger.info(
        "Searching through members that are on the archive server but are not in the database")

    # Search through members that are on the server but are not in the database
    for i, member in enumerate(guild_members):
        logger.info(
            f"Member {member.name} @{member.id} not in the database [{i}/{len(guild_members)}]")

        joined_at = member.joined_at
        if joined_at is None:  # From the discord.py docs "In certain cases, this can be None"
            joined_at = datetime.now()

        # If the member has rejoined the field joined_at from Discord.Member is reseted.
        # So we check the date of member's first message sent in the server
        try:
            first_message_date = await get_first_message_date(member.id, guild.id)
            first_join = min(first_message_date, joined_at)
        except KeyError:
            first_join = joined_at

        member_left = False
        if main_guild.get_member(member.id) is None:
            member_left = True

        save_member(Member(member.id, member.name, 0,
                           first_join=first_join, last_join=joined_at, member_left=member_left))
        await asyncio.sleep(0.5)

    logger.info("sync_database: Done")
    await msg.channel.send("sync_database: Done")


async def get_first_message_date(user_id: int, guild_id: int) -> datetime:
    selfbot = Selfbot(GlobalValues.get('selfbot_token'))
    message = await selfbot.client.get_first_message_in_guild(guild_id, user_id)
    if message is None:
        raise KeyError("No message was found")
    logger.info(f"Date of user's first message: {message.created_at}")
    return message.created_at
