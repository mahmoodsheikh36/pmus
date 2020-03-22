#!/bin/sh

music_object_type="${1:-song}"
action="${2:-play}" # available options: add, play

rofi_out="$(music_daemon_cmd.sh list $music_object_type\
    | sort -n | rofi -dmenu -i -p ${music_object_type}s -multi-select)"

# for now expand only works with albums, will be compatible with other
# song lists in the future
if [ $? -eq 10 ] && [ "$music_object_type" = "album" ]; then
    id=$(echo "$rofi_out" | cut -d ' ' -f1 | head -1)
    rofi_out="$(music_daemon_cmd.sh list ${music_object_type} $id\
        | sort -n | rofi -dmenu -i -p songs -multi-select)"
    music_object_type="song"
fi

ids=""
for id in "$(echo "$rofi_out" | cut -d ' ' -f1)"; do
    ids="$ids $id"
done

if [ "$music_object_type" = "liked" ]; then music_object_type="song"; fi
music_daemon_cmd.sh $action $music_object_type $ids
