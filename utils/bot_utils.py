import json

VARS:dict = None

def load_vars():
    with open('config.json', 'r') as config_file:
        global VARS
        VARS = json.load(config_file)

def get_ids(role_name: str):
    return [dic.get(role_name) for dic in VARS['guilds'] if dic.get(role_name) is not None]

def get_global(value_name: str):
    return VARS['global'][value_name]

def get_id_guild(value_name: str, guild_id: int):
    for v in VARS['guilds']:
        if v['id'] == guild_id:
            return v[value_name]
    
    raise ValueError(f"Value with name \"{value_name}\" does not exist")

def get_main_guild_id() -> int:
    for guild in VARS['guilds']:
        if guild['name'] == "main_guild":
            return guild['id']

def get_postgres_credentials() -> dict:
    vars = VARS['postgres']
    return {
        "host": vars['host'],
        "port": vars['port'],
        "database": vars['database'],
        "user": vars['user'],
        "password": vars['password']
    }