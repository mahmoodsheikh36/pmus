import sqlite3
import os.path
import os
import psutil

from pmus.ffmpeg import get_audio_format
from pmus.music import Song, Album, Artist, Playback
from pmus.utils import current_time, file_exists
from pmus.config import config

AUDIO_FILE_EXTENSIONS = ['mp3', 'flac', 'opus', 'm4a']

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
    def __init__(self, db_path=config.database_path):
        self.path = db_path
        should_create_db = False
        if not file_exists(self.path):
            should_create_db = True
        self.conn = self.get_new_conn()
        if should_create_db:
            self.create_db()

    def create_db(self):
        self.conn.executescript(get_schema_buffer())

    def cursor(self):
        return self.conn.cursor()

    def add_song(self, name, audio_url, duration):
        c = self.cursor()
        c.execute('INSERT INTO songs\
                   (name, audio_url, duration, time)\
                   VALUES (?, ?, ?, ?)',
                   (name, audio_url, duration, current_time()))
        return c.lastrowid

    def add_song_artist(self, song_id, artist_id):
        c = self.cursor()
        c.execute('INSERT INTO song_artists\
                   (artist_id, song_id)\
                   VALUES (?, ?)',
                   (artist_id, song_id))

    def add_album_artist(self, album_id, artist_id):
        c = self.cursor()
        c.execute('INSERT INTO album_artists\
                   (artist_id, album_id)\
                   VALUES (?, ?)',
                   (artist_id, album_id))

    def add_album_song(self, song_id, album_id, index_in_album):
        c = self.cursor()
        c.execute('INSERT INTO album_songs\
                   (song_id, album_id, index_in_album)\
                   VALUES (?, ?, ?)',
                   (song_id, album_id, index_in_album))

    def add_album(self, name, year):
        c = self.cursor()
        c.execute('INSERT INTO albums\
                   (name, year, time)\
                   VALUES (?, ?, ?)',
                   (name, year, current_time()))
        return c.lastrowid

    def add_artist(self, name):
        c = self.cursor()
        c.execute('INSERT INTO artists\
                   (name, time)\
                   VALUES (?, ?)',
                   (name, current_time()))
        return c.lastrowid

    def add_liked_song(self, song_id):
        self.cursor().execute('INSERT INTO liked_songs\
                               (song_id, time)\
                               VALUES (?, ?)',
                              (song_id, current_time()))
        self.commit()

    def add_playback(self, time_started, time_ended, song_id):
        c = self.cursor()
        c.execute('INSERT INTO playbacks\
                   (time_started, time_ended, song_id)\
                   VALUES (?, ?, ?)',
                  (time_started, time_ended, song_id))
        self.commit()
        return c.lastrowid

    def add_pause(self, time, playback_id):
        self.cursor().execute('INSERT INTO pauses\
                               (time, playback_id)\
                               VALUES (?, ?)',
                              (time, playback_id))
        self.commit()

    def add_resume(self, time, playback_id):
        self.cursor().execute('INSERT INTO resumes\
                               (time, playback_id)\
                               VALUES (?, ?)',
                              (time, playback_id))
        self.commit()

    def add_seek(self, time, position, playback_id):
        self.cursor().execute('INSERT INTO seeks\
                               (time, position, playback_id)\
                               VALUES (?, ?, ?)',
                              (time, position, playback_id))
        self.commit()

    def get_playbacks(self):
        return self.cursor().execute('SELECT * FROM playbacks').fetchall()

    def get_pauses(self):
        return self.cursor().execute('SELECT * FROM pauses').fetchall()

    def get_resumes(self):
        return self.cursor().execute('SELECT * FROM resumes').fetchall()

    def get_seeks(self, playback_id):
        c = self.cursor()
        return c.execute('SELECT * FROM seeks WHERE playback_id = ?',
                         (playback_id,)).fetchall()

    def get_new_conn(self):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = dict_factory
        return conn

    def update_playback_time_ended(self, playback_id, time_ended):
        c = self.cursor()
        c.execute('UPDATE playbacks SET\
                   time_ended = ?\
                   WHERE id = ?',
                  (time_ended, playback_id))
        self.conn.commit()

    def get_artist(self, artist_id):
        c = self.cursor()
        return c.execute('SELECT * FROM artists WHERE id = ?',
                         (artist_id,)).fetchone()

    def get_album(self, album_id):
        c = self.cursor()
        return c.execute('SELECT * FROM albums WHERE id = ?',
                         (album_id,)).fetchone()

    def get_song(self, song_id):
        c = self.cursor()
        return c.execute('SELECT * FROM songs WHERE id = ?',
                         (song_id,)).fetchone()

    def get_artist_by_name(self, artist_name):
        return self.cursor().execute('SELECT * FROM artists WHERE name = ?',
                                     (artist_name,)).fetchone()

    def get_album_by_name(self, album_name, artist_id):
        return self.cursor().execute('SELECT * FROM albums WHERE name = ? AND\
                                      id IN (select album_id from album_artists\
                                      WHERE artist_id = ?)',
                                     (album_name, artist_id)).fetchone()

    def get_album_song_by_idx(self, album_id, idx_in_album):
        return self.cursor().execute('SELECT * FROM album_songs WHERE album_id = ? AND\
                                      index_in_album = ?',
                                     (album_id, idx_in_album)).fetchone()

    def song_with_audio_url_exists(self, url):
        return self.cursor().execute('SELECT id FROM songs WHERE audio_url = ?',
                                     (url,)).fetchone() is not None

    def get_songs(self):
        return self.cursor().execute('SELECT id,name,time,audio_url,duration\
                                      FROM songs').fetchall()

    def get_artists(self):
        return self.cursor().execute('SELECT * FROM artists').fetchall()

    def get_albums(self):
        return self.cursor().execute('SELECT * FROM albums').fetchall()

    def get_album_artists(self):
        return self.cursor().execute('SELECT * FROM album_artists').fetchall()

    def get_song_artists(self):
        return self.cursor().execute('SELECT * FROM song_artists').fetchall()

    def get_album_songs(self):
        return self.cursor().execute('SELECT * FROM album_songs').fetchall()

    def is_song_liked(self, song_id):
        liked_song_row = self.cursor().execute('SELECT * FROM liked_songs\
                                      WHERE song_id = ?', (song_id,)).fetchone()
        return liked_song_row is not None

    def get_liked_songs(self):
        return self.cursor().execute('SELECT * FROM liked_songs').fetchall()

    def get_playback(self, playback_id):
        return self.cursor().execute('SELECT * FROM playbacks WHERE id = ?',
                         (playback_id,)).fetchone()

    def set_song_lyrics(self, song_id, lyrics):
        self.cursor().execute('UPDATE songs SET lyrics = ? WHERE id = ?',
                              (lyrics, song_id))

    def get_song_lyrics(self, song_id):
        return self.cursor().execute('SELECT lyrics FROM songs WHERE id = ?',
                         (song_id,)).fetchone()['lyrics']

    def commit(self):
        self.conn.commit()

class MusicProvider:
    def __init__(self):
        self.db_provider = DBProvider()
        self.songs = {}
        self.albums = {}
        self.singles = {}
        self.artists = {}
        self.playbacks = {}

    def unload_music(self):
        self.songs = {}
        self.albums = {}
        self.singles = {}
        self.artists = {}
        self.playbacks = {}

    def load_music(self):
        db_songs = self.db_provider.get_songs()
        db_artists = self.db_provider.get_artists()
        db_albums = self.db_provider.get_albums()
        db_song_artists = self.db_provider.get_song_artists()
        db_album_artists = self.db_provider.get_album_artists()
        db_album_songs = self.db_provider.get_album_songs()
        db_liked_songs = self.db_provider.get_liked_songs()
        db_playbacks = self.db_provider.get_playbacks()
        db_pauses = self.db_provider.get_pauses()
        db_resumes = self.db_provider.get_resumes()

        for db_artist in db_artists:
            artist = Artist(db_artist['id'], db_artist['name'], [], [])
            self.artists[artist.id] = artist

        for db_song in db_songs:
            song = Song(db_song['id'], db_song['audio_url'], db_song['name'],
                        [], db_song['duration'], playbacks=[])
            self.songs[song.id] = song

        for db_album in db_albums:
            album = Album(db_album['id'], db_album['name'], [],
                          [], db_album['year'])
            self.albums[album.id] = album

        for db_album_artist in db_album_artists:
            album_id = db_album_artist['album_id']
            artist_id = db_album_artist['artist_id']
            self.artists[artist_id].albums.append(self.albums[album_id])
            self.albums[album_id].artists.append(self.artists[artist_id])

        for db_song_artist in db_song_artists:
            song_id = db_song_artist['song_id']
            artist_id = db_song_artist['artist_id']
            self.songs[song_id].artists.append(self.artists[artist_id])

        for db_album_song in db_album_songs:
            song_id = db_album_song['song_id']
            album_id = db_album_song['album_id']
            self.albums[album_id].songs.append(self.songs[song_id])
            self.songs[song_id].album = self.albums[album_id]
            self.songs[song_id].index_in_album = db_album_song['index_in_album']

        for db_liked_song in db_liked_songs:
            song_id = db_liked_song['song_id']
            self.songs[song_id].time_liked = db_liked_song['time']

        # remove songs/albums that were deleted/moved from filesystem
        for album in list(self.albums.values()):
            for song in list(album.songs):
                if not file_exists(song.audio_url):
                    album.songs.remove(song)
                    del self.songs[song.id]
            if not album.songs:
                del self.albums[album.id]

        # sort songs in album by their index in it
        for album in self.albums.values():
            for i in range(len(album.songs)):
                for j in range(i + 1, len(album.songs)):
                    if album.songs[j].index_in_album < album.songs[i].index_in_album:
                        album.songs[i], album.songs[j] = album.songs[j], album.songs[i]

        for db_playback in db_playbacks:
            playback = Playback(db_playback['id'],
                                db_playback['song_id'],
                                db_playback['time_started'],
                                db_playback['time_ended'],
                                [], [])
            self.playbacks[db_playback['id']] = playback
            if db_playback['song_id'] in self.songs:
                self.songs[db_playback['song_id']].playbacks.append(playback)

        for db_pause in db_pauses:
            self.playbacks[db_pause['playback_id']].pauses.append(db_pause)

        for db_resume in db_resumes:
            self.playbacks[db_resume['playback_id']].pauses.append(db_resume)

    def on_audio_file_found(self, filepath):
        for song in self.songs.values():
            if song.audio_url == filepath:
                return
        audio_format = get_audio_format(filepath)
        if not 'tags' in audio_format:
            return
        tags = audio_format['tags']
        if not 'artist' in tags or not 'title' in tags:
            return

        artist_names = [tag.strip() for tag in tags['artist'].split(',')]
        album_artist_names = artist_names
        if 'album_artist' in tags:
            album_artist_names = [tag.strip() for tag in tags['album_artist'].split(',')]
        song_name = tags['title']

        db_artists = []
        for artist_name in artist_names:
            db_artist = self.db_provider.get_artist_by_name(artist_name)
            if db_artist is None:
                self.db_provider.add_artist(artist_name)
                db_artist = self.db_provider.get_artist_by_name(artist_name)
            db_artists.append(db_artist)

        if 'album' in tags:
            if not 'track' in tags:
                return
            idx_in_album = tags['track'].split('/')[0]
            album_name = tags['album']
            album_year = None
            if 'date' in tags:
                album_year = tags['date']
            db_album_artists = []
            for db_album_artist_name in album_artist_names:
                db_album_artist = self.db_provider.get_artist_by_name(db_album_artist_name)
                if db_album_artist is None:
                    self.db_provider.add_artist(db_album_artist_name)
                    db_album_artist = self.db_provider.get_artist_by_name(db_album_artist_name)
                db_album_artists.append(db_album_artist)
            db_album = self.db_provider.get_album_by_name(album_name,
                    db_album_artists[0]['id'])
            album_id = None
            if db_album is None:
                album_id = self.db_provider.add_album(album_name, album_year)
                for db_album_artist in db_album_artists:
                    self.db_provider.add_album_artist(album_id, db_album_artist['id'])
                print('added album {} - {}'.format(album_name, db_album_artists[0]['name']))
            else:
                album_id = db_album['id']
                old_album_song = self.db_provider.get_album_song_by_idx(album_id, idx_in_album)
                if old_album_song is not None:
                    old_song = self.db_provider.get_song(old_album_song['song_id'])
                    if old_album_song is not None and file_exists(old_song['audio_url']):
                        return
            song_id = self.db_provider.add_song(song_name, filepath, audio_format['duration'])
            for db_artist in db_artists:
                self.db_provider.add_song_artist(song_id, db_artist['id'])
            self.db_provider.add_album_song(song_id, album_id, idx_in_album)
        #else:
            #print('adding single {}'.format(song_name))

    def find_music(self, music_dir=config.music_dir):
        for folder, subs, files in os.walk(music_dir):
            if not '/trash' in folder:
                for filename in files:
                    is_audio_file = False
                    for audio_ext in AUDIO_FILE_EXTENSIONS:
                        if filename.endswith('.' + audio_ext):
                            is_audio_file = True
                    if not is_audio_file:
                        continue
                    filepath = os.path.join(folder, filename)
                    self.on_audio_file_found(filepath)
        self.db_provider.commit()

    def get_songs_list(self):
        return list(self.songs.values())

    def get_albums_list(self):
        return list(self.albums.values())

    def get_artists_list(self):
        return list(self.artists.values())
    
    def get_playbacks_list(self):
        return list(self.playbacks.values())

    def like_song(self, song):
        if self.db_provider.is_song_liked(song.id):
            return
        self.db_provider.add_liked_song(song.id)
        song.time_liked = current_time()
