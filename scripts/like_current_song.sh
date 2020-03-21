#!/bin/sh
# a script to like the current song that i am listening to and add it to
# the liked songs list in the remote database

current_song_id="$(music_daemon_cmd.sh current | cut -d ' ' -f1)"

if [ -z "$current_song_id" ]; then
    notify-send 'no song playing'
else
    success=$(curl -s -X POST "http://10.0.0.54/music/like_song?id=$current_song_id"\
        -F username=mahmooz -F password=mahmooz | jq .success)
    if [ "$success" = "false" ]; then
        notify-send 'song liked already'
    else
        notify-send 'liked song'
    fi
fi
