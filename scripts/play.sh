#!/bin/sh

music_object_type="${1:-song}"

dmenu_out="$(music_daemon_cmd.sh list $music_object_type\
    | sort -n | rofi -dmenu -i -p ${music_object_type}s -multi-select)"

ids=""
for id in "$(echo "$dmenu_out" | cut -d ' ' -f1)"; do
    ids="$ids $id"
done
music_daemon_cmd.sh play $music_object_type $ids
