#!/usr/bin/sh

song_id="$1"
song_path=$(pmus -I -F url -S $song_id -o song)
song_name=$(pmus -I -F name -S $song_id -o song)
artist_album=$(pmus -I -F 'artist_name - album_name' -S $song_id -o song)
echo $song_path
ffmpeg -y -loglevel panic -i "$song_path" /tmp/song_image.png && {
    notify-send -i /tmp/song_image.png "$song_name" "$artist_album"
}
