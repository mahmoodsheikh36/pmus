#!/usr/bin/sh
# script to show album art from pmus in sxiv and make it playable
# using various keys, might be slow because it uses ffmpeg to extract
# art from audio files, im considering caching images to make it faster

generate_art() {
    album_id=$1
    # using raw commands cuz i havent implemented a specifier for album ids yet
    first_track_id=$(pmus -r "list album $album_id" | head -1\
        | cut -d ' ' -f1 2>/dev/null)
    track_url=$(pmus -o track -S $first_track_id -I url)
    ffmpeg -y -i "$track_url" /tmp/art/"$(basename "$track_url")".png 2>/dev/null
}

if [ -d /tmp/art ]; then rm /tmp/art/*; else mkdir /tmp/art; fi 2>/dev/null

liked_albums="$(pmus -o album --specifier liked --info 'id ')"

for album_id in $liked_albums; do
    generate_art $album_id
    echo got art for $album_id
done
sxiv /tmp/art/
