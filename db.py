import requests
import json
import sqlite3
from music import Song, Album, Artist

def get_cache_dir():
    from pathlib import Path
    return str(Path.home()) + '/.cache/music_daemon/'

class DbProvider:
    def __init__(self, db_path=get_cache_dir()+'music.db'):
        self.path = db_path
        self.conn = sqlite3.connect(self.path)

    def add_song(self, name, audio_file_id, duration, bitrate, codec):
        c = self.conn.cursor()
        c.execute('INSERT INTO songs\
                   (name, audio_file_id, duration, bitrate, codec)\
                   VALUES (?, ?, ?, ?, ?)',
                   (name, audio_file_id, duration, bitrate, codec))

    def commit(self):
        self.conn.commit()

class MusicProvider:
    def __init__(self, username=None, password=None, backend_url='http://localhost'):
        self.backend = backend_url
        self.username = username
        self.password = password

    def music(self,):
        response = requests.get(
                '{}/music/metadata'.format(self.backend)
        ).text
        return self.handle_metadata(response)

    def handle_metadata(self, metadata_text):
        metadata = json.loads(metadata_text)

        # map each album, artist, song to its id to make lookup faster
        album_metadata_map  = {}
        artist_metadata_map = {}
        song_metadata_map  = {}

        # maps album ids to their album_song objects
        album_songs_map = {}
        # maps song ids to their artist_song objects
        song_artists_map = {}
        # map artist id to their album objects
        album_artists_map = {}

        for album in metadata['albums']:
            album_metadata_map[album['id']] = album
        for artist in metadata['artists']:
            artist_metadata_map[artist['id']] = artist
        for song in metadata['songs']:
            song_metadata_map[song['id']] = song

        for album_song in metadata['album_songs']:
            if album_song['album_id'] not in album_songs_map:
                album_songs_map[album_song['album_id']] = [album_song]
            else:
                album_songs_map[album_song['album_id']].append(album_song)

        for artist_song in metadata['song_artists']:
            if artist_song['song_id'] not in song_artists_map:
                song_artists_map[artist_song['song_id']] = [artist_song]
            else:
                song_artists_map[artist_song['song_id']].append(artist_song)

        for artist_album in metadata['album_artists']:
            if artist_album['album_id'] not in album_artists_map:
                album_artists_map[artist_album['album_id']] = [artist_album]
            else:
                album_artists_map[artist_album['album_id']].append(artist_album)

        artists_map = {}
        songs_map = {}
        singles = []
        albums = []

        for artist_metadata in metadata['artists']:
            artist = Artist(artist_metadata['id'],
                            artist_metadata['name'],
                            [],
                            [])
            artists_map[artist.id] = artist

        for song_metadata in metadata['songs']:
            song = Song(song_metadata['id'],
                        song_metadata['name'],
                        [],
                        song_metadata['audio_file_id'])
            songs_map[song.id] = song
            for song_artist in song_artists_map[song.id]:
                artist = artists_map[song_artist['artist_id']]
                song.artists.append(artist)

        for album_metadata in metadata['albums']:
            album = Album(album_metadata['id'],
                          album_metadata['name'],
                          [],
                          [],
                          album_metadata['year'],
                          album_metadata['image_file_id'])
            for album_artist in album_artists_map[album.id]:
                artist = artists_map[album_artist['artist_id']]
                album.artists.append(artist)
                artist.albums.append(album)
            for album_song in album_songs_map[album.id]:
                song = songs_map[album_song['song_id']]
                album.songs.append(song)
                song.album = album
            albums.append(album)

        for single_song_metadata in metadata['single_songs']:
            single_song = songs_map[single_song_metadata['song_id']]
            for artist in single_song.artists:
                artist.singles.append(single_song)
            singles.append(single_song)
                
        return list(songs_map.values()),\
               albums,\
               singles,\
               list(artists_map.values())
