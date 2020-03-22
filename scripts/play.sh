#!/bin/sh

music_object_type="${1:-song}"
action="${2:-play}" # available options: add, play

dmenu_out="$(music_daemon_cmd.sh list $music_object_type\
    | sort -n | rofi -dmenu -i -p ${music_object_type}s -multi-select)"

ids=""
for id in "$(echo "$dmenu_out" | cut -d ' ' -f1)"; do
    ids="$ids $id"
done

if [ "$music_object_type" = "liked" ]; then music_object_type="song"; fi
music_daemon_cmd.sh $action $music_object_type $ids
