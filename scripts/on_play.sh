#!/usr/bin/sh

song_id="$1"
song_path=$(md.py -I url -S $song_id -o song)
song_name=$(md.py -I name -S $song_id -o song)
artist_album=$(md.py -I 'artist_name - album_name' -S $song_id -o song)
echo $song_path
ffmpeg -y -loglevel panic -i "$song_path" /tmp/song_image.png && {
    notify-send -i /tmp/song_image.png "$song_name" "$artist_album"
}
