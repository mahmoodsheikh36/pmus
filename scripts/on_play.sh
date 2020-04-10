#!/usr/bin/sh

song_id="$1"
song_path=$(md.py -r "info song $song_id url")
song_name=$(md.py -r "info song $song_id name")
artist_name=$(md.py -r "info song $song_id artist")
ffmpeg -y -loglevel panic -i "$song_path" /tmp/song_image.png && {
    notify-send -i /tmp/song_image.png "$song_name" "$artist_name"
}
