#!/usr/bin/python3
import sys
import signal
import argparse
import subprocess
from pathlib import Path

from pmus.client import cmd_to_stdout, send_cmd_wait_all
from pmus.config import config

# fix broken pipes
from signal import SIGPIPE, SIG_DFL
signal.signal(SIGPIPE,SIG_DFL)

def start_server():
    from pmus.player import MusicPlayer
    from pmus.db import MusicProvider
    from pmus.server import Server
    provider = MusicProvider()
    provider.load_music()
    print('music loaded')

    player = MusicPlayer()
    server = Server(player, provider)

    def on_exit(signum=None, frame=None):
        print('terminating...')
        server.terminate()
        print('done')
        sys.exit(0)

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    server.start()

def extract_art_from_url(url, art_filename, out_dir):
    return_code = subprocess.call(['ffmpeg', '-y', '-i', url, '{}/{}'.format(
        out_dir, art_filename), '-loglevel', 'quiet'])
    return return_code == 0

def generate_art(music_obj, specifier, filename_format, out_dir, limit):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if music_obj == 'album':
        all_album_info = send_cmd_wait_all('info {} {} {} {} {}'.format(music_obj,
            specifier, 'id', limit,
            'first_audio_url\t{}\n'.format(filename_format)))
        for album_info in all_album_info.split('\n'):
            if album_info == '': # ignore empty line after last \n
                continue
            first_audio_url = album_info.split('\t')[0]
            art_filename = '{}.png'.format(album_info.split('\t')[1])
            if extract_art_from_url(first_audio_url, art_filename, out_dir):
                print(art_filename)
    elif music_obj == 'song':
        all_song_info = send_cmd_wait_all('info {} {} {} {} {}'.format(
            music_obj, specifier, 'id', limit, 'url\t{}\n'.format(filename_format)))
        for song_info in all_song_info.split('\n'):
            if song_info == '': # ignore empty line after last \n
                continue
            audio_url = song_info.split('\t')[0]
            art_filename = '{}.png'.format(song_info.split('\t')[1])
            if extract_art_from_url(audio_url, art_filename, out_dir):
                print(art_filename)
    elif music_obj == 'artist':
        all_artist_info = send_cmd_wait_all('info {} {} {} {} {}'.format(
            music_obj, specifier, 'id', limit,
            'first_audio_url\t{}\n'.format(filename_format)))
        for artist_info in all_artist_info.split('\n'):
            if artist_info == '': # ignore empty line after last \n
                continue
            audio_url = artist_info.split('\t')[0]
            art_filename = '{}.png'.format(artist_info.split('\t')[1])
            if extract_art_from_url(audio_url, art_filename, out_dir):
                print(art_filename)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='a simple and highly extensible music daemon')
    parser.add_argument('-o', '--object', metavar='music_object', type=str,
                        help='the music object type to do action on',
                        dest='music_object', choices=('playlist',
                                                      'song',
                                                      'album',
                                                      'liked',
                                                      'artist'))
    parser.add_argument('-p', '--play',
                        help='play objects of type specified by -o/--object',
                        action='store_true')
    parser.add_argument('-d', '--daemon', help='start the server/daemon',
                        action='store_true')
    parser.add_argument('-r', '--raw_cmd', metavar='raw command',
                        help='send a raw command to the server/daemon')
    parser.add_argument('-S', '--specifier', nargs='?', default='all',
                        help='the specifier, could be a list of song ids')
    parser.add_argument('-c', '--current', action='store_true',
                        dest='print_current_song',
                        help='print the current song (that is playing)')
    parser.add_argument('-f', '--find_music', nargs='?', const=config.music_dir,
                        help='tell the daemon to look for music')
    parser.add_argument('-I', '--info', action='store_true',
                        help='get info about objects of type specified by -o and -S, choose output format using -F')
    parser.add_argument('-F', '--output_format', nargs='?', default='id,name\n',
                        help='output format')
    parser.add_argument('-s', '--sort_by', help='what to sort music objects by', 
                        choices=('time_liked', 'name', 'id'), default='id')
    parser.add_argument('-P', '--port', help='network port to listen on',
                        type=int)
    parser.add_argument('-H', '--host', help='network host to listen on')
    parser.add_argument('-l', '--limit', help='specify the limit of the amount of objects to act on, default value 0 which means no limit', nargs='?', default=0)
    parser.add_argument('-ga', '--generate_art', help='generate art for objects selected using -o,-S')
    args = parser.parse_args()

    if args.daemon:
        print('running as a daemon')
        start_server()

    if args.port:
        config.port = args.port
    if args.host:
        config.host = args.host

    if args.raw_cmd:
        cmd_to_stdout(args.raw_cmd)
    else:
        if args.find_music:
            cmd_to_stdout('find_music {}'.format(args.find_music))
        elif args.music_object:
            if args.info: # args.info contains the info format
                cmd_to_stdout('info {} {} {} {} {}'.format(args.music_object,
                                                           args.specifier,
                                                           args.sort_by,
                                                           args.limit,
                                                           args.output_format))
            elif args.play:
                cmd_to_stdout('play {} {}'.format(args.music_object,
                                                  args.specifier.replace(',', ' ')))
            elif args.generate_art:
                generate_art(args.music_object, args.specifier,
                             args.output_format, args.generate_art, args.limit)
            else:
                parser.print_help()
        elif args.print_current_song:
            cmd_to_stdout('current')
        else:
            parser.print_help()
