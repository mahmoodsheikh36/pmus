import requests
import json
import sqlite3
import os.path
from music_daemon.music import Song, Album, Artist, MusicLibrary
from pathlib import Path

def get_cache_dir():
    path = str(Path.home()) + '/.cache/music_daemon/'
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def get_db_path():
    return get_cache_dir() + 'music.db'

def get_schema_buffer():
    project_directory_path = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(project_directory_path, 'schema.sql')) as schema_file:
        return schema_file.read()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DBProvider:
    def __init__(self, db_path=get_cache_dir()+'music.db'):
        self.path = db_path
        should_create_db = False
        if not Path(self.path).is_file():
            should_create_db = True
        self.conn = self.get_new_conn()
        if should_create_db:
            self.create_db()

    def create_db(self):
        self.conn.executescript(get_schema_buffer())

    def add_song(self, song_id, name, audio_file_id, duration, bitrate, codec):
        c = self.conn.cursor()
        c.execute('INSERT INTO songs\
                   (id, name, audio_file_id, duration, bitrate, codec)\
                   VALUES (?, ?, ?, ?, ?, ?)',
                   (song_id, name, audio_file_id, duration, bitrate, codec))

    def add_song_artist(self, row_id, artist_id, song_id):
        c = self.conn.cursor()
        c.execute('INSERT INTO song_artists\
                   (id, artist_id, song_id)\
                   VALUES (?, ?, ?)',
                   (row_id, artist_id, song_id))

    def add_album_artist(self, row_id, artist_id, album_id):
        c = self.conn.cursor()
        c.execute('INSERT INTO album_artists\
                   (id, artist_id, album_id)\
                   VALUES (?, ?, ?)',
                   (row_id, artist_id, song_id))

    def add_album_song(self, row_id, song_id, album_id, index_in_album):
        c = self.conn.cursor()
        c.execute('INSERT INTO album_songs\
                   (id, song_id, album_id, index_in_album)\
                   VALUES (?, ?, ?, ?)',
                   (row_id, song_id, album_id, index_in_album))

    def add_single_song(self, row_id, song_id, image_file_id, year, time_added):
        c = self.conn.cursor()
        c.execute('INSERT INTO single_songs\
                   (id, song_id, image_file_id, year, time_added)\
                   VALUES (?, ?, ?, ?, ?)',
                   (row_id, song_id, image_file_id, year, time_added))

    def add_album(self, album_id, name, image_file_id, year, time_added):
        c = self.conn.cursor()
        c.execute('INSERT INTO albums\
                   (id, name, year, image_file_id, time_added)\
                   VALUES (?, ?, ?, ?, ?)',
                   (album_id, name, year, image_file_id, time_added))

    def add_artist(self, artist_id, name):
        c = self.conn.cursor()
        c.execute('INSERT INTO artists\
                   (id, name)\
                   VALUES (?, ?)',
                   (artist_id, name))

    def add_artist_image(self, row_id, artist_id, image_file_id):
        c = self.conn.cursor()
        c.execute('INSERT INTO artist_images\
                   (id, image_file_id, artist_id)\
                   VALUES (?, ?, ?)',
                   (row_id, image_file_id, artist_id))

    def add_liked_song(self, row_id, song_id, time_added):
        c = self.conn.cursor()
        c.execute('INSERT INTO liked_songs\
                   (id, song_id, time_added)\
                   VALUES (?, ?, ?)',
                   (row_id, song_id, time_added))

    def add_playback(self, time_started, time_ended, song_id):
        # see note for update_playback_time_ended function
        conn = self.get_new_conn()
        c = conn.cursor()
        c.execute('INSERT INTO playbacks\
                   (time_started, time_ended, song_id)\
                   VALUES (?, ?, ?)',
                  (time_started, time_ended, song_id))
        # i guess gotta commit to get the lastrowid since we need it
        conn.commit()
        return c.lastrowid

    def add_pause(self, time, playback_id):
        # see note for update_playback_time_ended function
        conn = self.get_new_conn()
        c = conn.cursor()
        c.execute('INSERT INTO pauses\
                   (time, playback_id)\
                   VALUES (?, ?)',
                  (time, playback_id))
        conn.commit()

    def add_resume(self, time, playback_id):
        # see note for update_playback_time_ended function
        conn = self.get_new_conn()
        c = conn.cursor()
        c.execute('INSERT INTO resumes\
                   (time, playback_id)\
                   VALUES (?, ?)',
                  (time, playback_id))
        conn.commit()

    def add_seek(self, time, position, playback_id):
        # see note for update_playback_time_ended function
        conn = self.get_new_conn()
        c = conn.cursor()
        c.execute('INSERT INTO seeks\
                   (time, position, playback_id)\
                   VALUES (?, ?, ?)',
                  (time, position, playback_id))
        conn.commit()

    def get_playbacks(self, song_id):
        c = self.conn.cursor()
        return c.execute('SELECT * FROM playbacks WHERE song_id = ?',
                         (song_id,)).fetchall()

    def get_pauses(self, playback_id):
        c = self.conn.cursor()
        return c.execute('SELECT * FROM pauses WHERE playback_id = ?',
                         (playback_id,)).fetchall()

    def get_resumes(self, playback_id):
        c = self.conn.cursor()
        return c.execute('SELECT * FROM resumes WHERE playback_id = ?',
                         (playback_id,)).fetchall()
        return c.lastrowid

    def get_seeks(self, playback_id):
        c = self.conn.cursor()
        return c.execute('SELECT * FROM seeks WHERE playback_id = ?',
                         (playback_id,)).fetchall()
        return c.lastrowid

    def get_new_conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = dict_factory
        return conn

    """
    always use a new connection when updating playbacks because this
    function is only run from a seperate thread (the AudioTask thread)
    and sqlite3 connections can only be used from the thread they
    were created in
    same goes for add_seek, add_pause, add_resume functions
    """
    def update_playback_time_ended(self, playback_id, time_ended):
        conn = self.get_new_conn()
        c = conn.cursor()
        c.execute('UPDATE playbacks SET\
                   time_ended = ?\
                   WHERE id = ?',
                  (time_ended, playback_id))
        conn.commit()

    def commit(self):
        self.conn.commit()

class MusicProvider:
    def __init__(self, username=None, password=None, backend_url='http://localhost'):
        self.db_provider = DBProvider()
        self.backend = backend_url
        self.username = username
        self.password = password

    def music(self):
        response = requests.get(
                '{}/music/metadata'.format(self.backend)
        ).text
        songs, albums, singles, artists = self.handle_metadata(response)
        return MusicLibrary(songs, artists, albums, singles)

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
                        self.get_file_url(song_metadata['audio_file_id']),
                        song_metadata['duration'],
                        song_metadata['sample_rate'],
                        song_metadata['channels'])
            song.seconds_listened = self.get_seconds_listened_to_song(song.id)
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

    def get_file_url(self, file_id):
        return '{}/static/file/{}'.format(self.backend, file_id)

    # FIXME: this is wrong, should make use of pauses,seeks,resumes
    def get_seconds_listened_to_song(self, song_id):
        playbacks = self.db_provider.get_playbacks(song_id)
        total_seconds = 0
        for playback in playbacks:
            if playback['time_ended'] == -1:
                continue
            seconds = (playback['time_ended'] - playback['time_started']) / 1000
            total_seconds += seconds
        return total_seconds
