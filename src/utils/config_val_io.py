import json

from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)

VALS = dict()
CONFIG_FILE = 'properties/config_v2.json'


class AllGuildVals:

    @staticmethod
    def get(val_name: str) -> list:
        global VALS
        if VALS == {}:
            load_vals()

        result_list = []
        for v in VALS:
            try:
                result_list.append((v['guild_id'], v[val_name]))
            except KeyError:
                continue

        return result_list


class GuildSpecificVals:
    @staticmethod
    def get(guild_id: int, val_name: str):
        global VALS
        if VALS == {}:
            load_vals()

        for v in VALS:
            if v['guild_id'] == guild_id:
                return v[val_name]

        raise KeyError(f"guild '{guild_id}' doesn't exist")

    @staticmethod
    def save(guild_id: int, val_name: str, val):
        global VALS
        if VALS == {}:
            load_vals()

        for v in VALS:
            if v['guild_id'] == guild_id:
                v[val_name] = val
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(VALS, f, ensure_ascii=False, indent=2)
                return

        raise KeyError(f"guild '{guild_id}' doesn't exist")


def load_vals():
    global VALS
    try:
        with open(CONFIG_FILE, 'r') as config_file:
            VALS = json.load(config_file)
    except Exception as error:
        logger.error(error)
