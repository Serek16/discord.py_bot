import discord
import pytesseract
import json
from time import sleep
from PIL import Image
import requests
from io import BytesIO

from src.selfbot.discum_bot import DiscumBot
from src.selfbot.slash_command import SlashCommand
from src.utils.logger import get_logger
from src.utils.config_val_io import GlobalValues, GuildSpecificValues

logger = get_logger(__name__, __name__)


def fetch_members_level(member: discord.Member, discum_bot: DiscumBot) -> int:
    guild_id = member.guild.id
    channel_id = GuildSpecificValues.get(guild_id, 'set_level_channel_id')
    arcane_id = GlobalValues.get('arcane_id')
    command_name = 'level'
    command_args = {'member': member.id}

    discum_bot.client.sendMessage(str(channel_id), "------")
    while True:
        discum_bot.send_slash_command(SlashCommand(guild_id, channel_id, arcane_id, command_name, command_args))

        sleep(1)

        byte_content = discum_bot.client.getMessages(str(channel_id), num=1).content
        obj_content = json.loads(byte_content.decode('utf-8'))[0]

        author_id = int(obj_content['author']['id'])

        if author_id != GlobalValues.get('arcane_id'):
            continue
        if obj_content['content'] == '':
            continue
        else:
            if obj_content['content'] == "❌ **You have no rank. Keep chatting to earn a rank!**":
                return 0
            if obj_content['attachments'][0]['url'] != {}:
                img_url = obj_content['attachments'][0]['url']
                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
                cropped_img = crop_level_info_image(img)
                return retrieve_level_from_image(cropped_img)


def crop_level_info_image(img: Image) -> Image:
    left = 140
    top = 90
    right = 250
    bottom = 50
    width, height = img.size
    return img.crop((left, top, width - right, height - bottom))


def retrieve_level_from_image(img: Image) -> int:
    img_msg = pytesseract.image_to_string(img)
    logger.debug(img_msg)
    level: str = \
        (img_msg.split("Level"))[1].split("XP")[0] \
        .replace(" ", "") \
        .replace("O", "0") \
        .replace("o", "0")
    level = ''.join(x for x in level if x.isdigit())
    if level == '':
        level = '0'
    return int(level)
