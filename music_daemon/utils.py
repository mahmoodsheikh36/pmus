import time
import subprocess
import os.path
import re
from pathlib import Path

# time since the unix epoch in milliseconds
current_time = lambda: int(round(time.time() * 1000))

def file_exists(filepath):
    return os.path.isfile(filepath)

def get_home_dir():
    return str(Path.home())

def multiple_replace(string, rep_dict):
    pattern = re.compile("|".join([re.escape(k) for k in sorted(rep_dict,key=len,reverse=True)]), flags=re.DOTALL)
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)
