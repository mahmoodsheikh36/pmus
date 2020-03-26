#!/bin/sh
# a script to like the current song that i am listening to and add it to
# the liked songs list in the remote database

current_song_id="$(music_daemon_cmd.sh current | cut -d ' ' -f1)"
music_daemon_cmd.sh like $current_song_id
notify-send "liked song $current_song_id"
