#!/usr/bin/python3
import sys
import signal
import argparse

from music_daemon.player import MusicPlayer
from music_daemon.db import MusicProvider
from music_daemon.server import Server
from music_daemon.client import cmd_to_stdout

def start_server():
    provider = MusicProvider()
    provider.load_music()

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
            description='friendly neighborhood music_daemon')
    parser.add_argument('-o', '--object', metavar='music_object', type=str,
                        help='the music object type to do action on',
                        dest='music_object', choices=('playlist',
                                                      'song',
                                                      'album',
                                                      'liked',
                                                      'artist'))
    parser.add_argument('-l', '--list',
                        help='list objects of type specified by -o/--object',
                        action='store_true')
    parser.add_argument('-p', '--play',
                        help='play objects of type specified by -o/--object',
                        action='store_true')
    parser.add_argument('-d', '--daemon', help='start the server/daemon',
                        action='store_true')
    parser.add_argument('-r', '--raw_cmd', metavar='raw command',
                        help='send a raw command to the server')
    parser.add_argument('-i', '--ids', metavar='raw command',
                        help='a comma-seperated list of ids of the music objects')
    parser.add_argument('-c', '--current', action='store_true',
                        dest='print_current_song',
                        help='print the current song (that is playing)')
    args = parser.parse_args()

    if args.daemon:
        print('running as a daemon')
        start_server()

    if args.raw_cmd:
        cmd_to_stdout(args.raw_cmd)
    else:
        if args.music_object:
            if args.list:
                cmd_to_stdout('list {}'.format(args.music_object))
            elif args.play:
                cmd_to_stdout('play {} {}'.format(args.music_object,
                                                  args.ids.replace(',', ' ')))
            else:
                parser.print_help()
        elif args.print_current_song:
            cmd_to_stdout('current')
        else:
            parser.print_help()
