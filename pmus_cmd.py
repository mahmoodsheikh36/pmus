#!/usr/bin/python3
import sys
import signal
import argparse

from pmus.client import cmd_to_stdout
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
    parser.add_argument('-S', '--specifier',
                        help='the specifier, could be a list of song ids')
    parser.add_argument('-c', '--current', action='store_true',
                        dest='print_current_song',
                        help='print the current song (that is playing)')
    parser.add_argument('-f', '--find_music', nargs='?', const=config.music_dir,
                        help='tell the daemon to look for music')
    parser.add_argument('-I', '--info', metavar='info format', nargs='?',
                        const='id name - album_name - artist_name\n',
                        help='get info about objects of type specified by -o/--object and specify which objects to select using -s/--specifier')
    parser.add_argument('-s', '--sort_by', help='what to sort music objects by', 
                        choices=('time_liked', 'name', 'id'))
    parser.add_argument('-P', '--port', help='network port to listen on',
                        type=int)
    parser.add_argument('-H', '--host', help='network host to listen on')
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
                cmd_to_stdout('info {} {} {} {}'.format(args.music_object,
                                                     args.specifier,
                                                     args.sort_by,
                                                     args.info))
            elif args.play:
                cmd_to_stdout('play {} {}'.format(args.music_object,
                                                  args.specifier.replace(',', ' ')))
            else:
                parser.print_help()
        elif args.print_current_song:
            cmd_to_stdout('current')
        else:
            parser.print_help()
