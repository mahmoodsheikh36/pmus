import subprocess
import json

def get_audio_format(filepath):
    format_map = json.loads(subprocess.check_output(
        ['ffprobe',
         '-loglevel',
         'panic',
         '-show_entries',
         'format_tags:format=duration',
         '-of',
         'json',
         filepath]))['format']
    if 'tags' in format_map:
        format_map['tags'] = {k.lower():v for k,v in format_map['tags'].items()}
    return format_map
