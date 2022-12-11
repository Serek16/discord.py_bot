import json
import yaml
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)

VALS = dict()
CONFIG_FILE = 'properties/config.json'
YAML_CONFIG_FILE = 'properties/config.yml'


class AggregatedGuildValues:

    @staticmethod
    def get(val_name: str) -> list:
        global VALS
        if VALS == {}:
            _load_from_file()

        result_list = list()
        for v in VALS:
            try:
                result_list.append((v['guild_id'], v[val_name]))
            except KeyError:
                continue

        return result_list


class GuildSpecificValues:

    @staticmethod
    def get(guild_id: int, val_name: str):
        if VALS == {}:
            _load_from_file()

        for v in VALS:
            if v['guild_id'] == guild_id:
                return v[val_name]

        raise KeyError(f"guild '{guild_id}' doesn't exist")

    @staticmethod
    def set(guild_id: int, val_name: str, val):
        if VALS == {}:
            _load_from_file()

        for v in VALS:
            if v['guild_id'] == guild_id:
                v[val_name] = val
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(VALS, f, ensure_ascii=False, indent=2)
                return

        raise KeyError(f"guild '{guild_id}' doesn't exist")


class GlobalValues:

    @staticmethod
    def get(val_name: str):
        with open(YAML_CONFIG_FILE, "r") as file:
            try:
                yaml_values: dict = yaml.safe_load(file)
                return yaml_values[val_name]
            except yaml.YAMLError as exc:
                logger.error(exc)


def _load_from_file():
    global VALS
    try:
        with open(CONFIG_FILE, 'r') as config_file:
            VALS = json.load(config_file)
    except Exception as error:
        logger.error(error)
