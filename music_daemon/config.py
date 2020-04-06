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
        config.DATABASE_PATH = config_json['database_path']
        config.MUSIC_DIR = config_json['music_directory']
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
    DATABASE_PATH = get_cache_dir() + '/music.db'
    MUSIC_DIR = get_home_dir() + '/music'

config = load_config()
