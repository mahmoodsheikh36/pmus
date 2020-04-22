#!/bin/sh

music_object_type="${1:-song}"
action="${2:-play}" # available options: add, play

[ $music_object_type = "liked" ] && {
    rofi_out="$(echo -n $(pmus -S liked -s time_liked -o song -I "id name - album_name - artist_name\n") |\
        rofi -async-pre-read 1 -dmenu -i -p "${music_object_type}s" -multi-select)"
} 
[ $music_object_type = "song" ] && {
    rofi_out="$(echo -n $(pmus -S all -s id -o song -I "id name - album_name - artist_name\n") |\
        rofi -async-pre-read 1 -dmenu -i -p "${music_object_type}s" -multi-select)"
}
[ $music_object_type = "album" ] && {
    rofi_out="$(echo -n $(pmus -S all -s id -o album -I "id name - artist\n") |\
        rofi -async-pre-read 1 -dmenu -i -p "${music_object_type}s" -multi-select)"
}

# for now expand only works with albums, will be made compatible with other
# song lists like playlists in the future
rofi_exit_code=$?
if [ $rofi_exit_code -eq 10 ] && [ "$music_object_type" = "album" ]; then
    id=$(echo "$rofi_out" | cut -d ' ' -f1 | head -1)
    rofi_out="$(pmus -r "list ${music_object_type} $id"\
        | rofi -async-pre-read 1 -dmenu -i -p songs -multi-select)"
    rofi_exit_code=$?
    music_object_type="song"
fi

[ $rofi_exit_code -eq 11 ] && action=play
[ $rofi_exit_code -eq 12 ] && action=add

ids=""
for id in "$(echo "$rofi_out" | cut -d ' ' -f1)"; do
    ids="$ids $id"
done

if [ "$music_object_type" = "liked" ]; then music_object_type="song"; fi
pmus -r "$action $music_object_type $ids"
