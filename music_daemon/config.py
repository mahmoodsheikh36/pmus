import json
from pathlib import Path
from music_daemon.utils import get_home_dir

def get_config_dir():
    return get_home_dir() + '/.config/music_daemon'

def get_config_file():
    return get_config_dir() + '/config.json'

def load_config():
    config = Config()
    try:
        with open(get_config_file(), 'r') as config_file:
            config_json = json.loads(config_file.read())
        config.database_path = config_json['database_path']
        config.music_dir = config_json['music_directory']
        config.port = int(config_json['port'])
        config.host = config_json['host']
    except Exception as e:
        print('error loading config file')
        print(e)
    finally:
        return config

def get_cache_dir():
    path = get_home_dir() + '/.cache/music_daemon/'
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

class Config:
    database_path = get_cache_dir() + '/music.db'
    music_dir = get_home_dir() + '/music'
    host = '0.0.0.0'
    port = 5150

config = load_config()