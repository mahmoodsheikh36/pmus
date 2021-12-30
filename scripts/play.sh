#!/bin/sh

music_object_type="${1:-track}"
action="${2:-play}" # available options: add, play

[ $music_object_type = "liked" ] && {
    rofi_out="$(pmus -S liked -s time_liked -o track -I -F "id name - album_name - artist_name
" |\
        rofi -async-pre-read 1 -dmenu -i -p "${music_object_type}s" -multi-select)"
} 
[ $music_object_type = "track" ] && {
    rofi_out="$(pmus -S all -s id -o track -I -F "id name - album_name - artist_name
" |\
        rofi -async-pre-read 1 -dmenu -i -p "${music_object_type}s" -multi-select)"
}
[ $music_object_type = "album" ] && {
    rofi_out="$(pmus -S all -s id -o album -I -F "id name - artist_name
" |\
        rofi -async-pre-read 1 -dmenu -i -p "${music_object_type}s" -multi-select)"
}

# for now expand only works with albums, will be made compatible with other
# track lists like playlists in the future
rofi_exit_code=$?
if [ $rofi_exit_code -eq 10 ] && [ "$music_object_type" = "album" ]; then
    id=$(echo "$rofi_out" | cut -d ' ' -f1 | head -1)
    rofi_out="$(pmus -I -s idx_in_album -o track -F "id name - album_name - artist_name
" -S album=$id\
        | rofi -async-pre-read 1 -dmenu -i -p tracks -multi-select)"
    rofi_exit_code=$?
    music_object_type="track"
fi

[ $rofi_exit_code -eq 11 ] && action=play
[ $rofi_exit_code -eq 12 ] && action=add

ids=""
ids=$(echo "$rofi_out" | cut -d ' ' -f1 | tr '\n' ' ' | rev |
    cut -d ' ' -f2- | rev)

if [ "$music_object_type" = "liked" ]; then music_object_type="track"; fi
[ "$ids" != "" ] && pmus -r "$action $music_object_type $ids"
