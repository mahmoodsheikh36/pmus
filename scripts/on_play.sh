#!/usr/bin/sh

track_id="$1"
track_path=$(pmus -I -F url -S $track_id -o track)
track_name=$(pmus -I -F name -S $track_id -o track)
artist_album=$(pmus -I -F 'artist_name - album_name' -S $track_id -o track)
echo $track_path
ffmpeg -y -loglevel panic -i "$track_path" /tmp/track_image.png && {
    notify-send -i /tmp/track_image.png "$track_name" "$artist_album"
}
