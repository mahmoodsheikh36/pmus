import time
import subprocess
import os.path
from pathlib import Path

# time since the unix epoch in milliseconds
current_time = lambda: int(round(time.time() * 1000))

def file_exists(filepath):
    return os.path.isfile(filepath)

def get_home_dir():
    return str(Path.home())
