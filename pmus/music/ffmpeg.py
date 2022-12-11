import subprocess
import json

def get_audio_format(filepath):
    all_map = json.loads(subprocess.check_output(
        ['ffprobe',
         '-loglevel',
         'panic',
         '-show_entries',
         'format_tags:stream_tags:format=duration',
         '-of',
         'json',
         filepath]))
    all_map['duration'] = all_map['format']['duration']
    all_map['tags'] = {}
    if 'tags' in all_map['format']:
        all_map['tags'] = {k.lower():v for k,v in all_map['format']['tags'].items()}
    # a bit of a hacky way to get all possible tags even from streams
    if 'streams' in all_map:
        for stream in all_map['streams']:
            for k,v in stream['tags'].items():
                all_map['tags'][k.lower()] = v
    return all_map
