#!/bin/sh
# a script to like the current song that i am listening to

current_song_id="$(pmus -r current | cut -d ' ' -f1)"
pmus -r "like $current_song_id"
notify-send "liked song $current_song_id"
