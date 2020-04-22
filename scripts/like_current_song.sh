#!/bin/sh
# a script to like the current song that i am listening to

current_song_id="$(pmus_cmd.sh current | cut -d ' ' -f1)"
pmus_cmd.sh like $current_song_id
notify-send "liked song $current_song_id"
