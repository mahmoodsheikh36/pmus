#!/usr/bin/python3
from pmus.client import send_cmd_wait_all
import subprocess

tmp_dir = '/tmp/art'

def get_albums():
    return send_cmd_wait_all(
            'info track liked time_liked album_id\talbum_name\tartist_name\turl\n')

def generate_art(album_id, album_name, artist_name, url):
    subprocess.call(['ffmpeg', '-y', '-i', url, '{}/{} - {} - {}.png'.format(
        tmp_dir, album_id, album_name, artist_name), '-loglevel', 'fatal'])

if __name__ == '__main__':
    # make sure tmp directory is created
    from pathlib import Path
    Path(tmp_dir).mkdir(exist_ok=True)

    albums = get_albums()
    albums_done = []
    for album in albums.split('\n'):
        if album == '': # nothing comes after last \n
            continue
        album_id = album.split('\t')[0]
        if album_id in albums_done: # we dont want duplicates
            continue
        albums_done.append(album_id)
        album_name = album.split('\t')[1]
        artist_name = album.split('\t')[2]
        url = album.split('\t')[3]
        generate_art(album_id, album_name, artist_name, url)
        print('generated art for {} - {}'.format(album_name, artist_name))
    subprocess.call(['sxiv', tmp_dir])
