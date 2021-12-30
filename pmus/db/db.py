import sqlite3
import os.path
import os

from pmus.music.music import Track, Album, Artist, Playback
from pmus.utils.config import config
from pmus.utils.utils import current_time, file_exists

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

    def add_track(self, name, album_id, audio_file_path, duration, index_in_album):
        c = self.cursor()
        c.execute('INSERT INTO tracks\
                   (name, album_id, audio_file_path, duration, time, index_in_album)\
                   VALUES (?, ?, ?, ?, ?, ?)',
                   (name, album_id, audio_file_path, duration, current_time(), index_in_album))
        return c.lastrowid

    def add_track_artist(self, track_id, artist_id):
        c = self.cursor()
        c.execute('INSERT INTO track_artists\
                   (artist_id, track_id)\
                   VALUES (?, ?)',
                   (artist_id, track_id))

    def add_album_artist(self, album_id, artist_id):
        c = self.cursor()
        c.execute('INSERT INTO album_artists\
                   (artist_id, album_id)\
                   VALUES (?, ?)',
                   (artist_id, album_id))

    def add_album(self, name, year):
        c = self.cursor()
        c.execute('INSERT INTO albums\
                   (name, year)\
                   VALUES (?, ?)',
                   (name, year))
        return c.lastrowid

    def add_artist(self, name):
        c = self.cursor()
        c.execute('INSERT INTO artists\
                   (name)\
                   VALUES (?)',
                   (name,))
        return c.lastrowid

    def add_playback(self, time_started, time_ended, track_id):
        c = self.cursor()
        c.execute('INSERT INTO playbacks\
                   (time_started, time_ended, track_id)\
                   VALUES (?, ?, ?)',
                  (time_started, time_ended, track_id))
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

    def get_track(self, track_id):
        c = self.cursor()
        return c.execute('SELECT * FROM tracks WHERE id = ?',
                         (track_id,)).fetchone()

    def get_artist_by_name(self, artist_name):
        return self.cursor().execute('SELECT * FROM artists WHERE name = ?',
                                     (artist_name,)).fetchone()

    def get_album_by_name(self, album_name, artist_id):
        return self.cursor().execute('SELECT * FROM albums WHERE name = ? AND\
                                      id IN (select album_id from album_artists\
                                      WHERE artist_id = ?)',
                                     (album_name, artist_id)).fetchone()

    def track_with_audio_file_path_exists(self, url):
        return self.cursor().execute('SELECT id FROM tracks WHERE audio_file_path = ?',
                                     (url,)).fetchone() is not None

    def get_tracks(self):
        return self.cursor().execute('SELECT id,name,time,audio_file_path,duration\
                                      FROM tracks').fetchall()

    def get_artists(self):
        return self.cursor().execute('SELECT * FROM artists').fetchall()

    def get_albums(self):
        return self.cursor().execute('SELECT * FROM albums').fetchall()

    def get_album_artists(self):
        return self.cursor().execute('SELECT * FROM album_artists').fetchall()

    def get_track_artists(self):
        return self.cursor().execute('SELECT * FROM track_artists').fetchall()

    def get_playback(self, playback_id):
        return self.cursor().execute('SELECT * FROM playbacks WHERE id = ?',
                         (playback_id,)).fetchone()

    def set_track_lyrics(self, track_id, lyrics):
        self.cursor().execute('UPDATE tracks SET lyrics = ? WHERE id = ?',
                              (lyrics, track_id))

    def get_track_lyrics(self, track_id):
        return self.cursor().execute('SELECT lyrics FROM tracks WHERE id = ?',
                         (track_id,)).fetchone()['lyrics']

    def commit(self):
        self.conn.commit()

    def get_track_by_album(self, album_id, index_in_album):
        return self.cursor().execute('SELECT * FROM tracks WHERE index_in_album = ? AND album_id = ?',
                                     (index_in_album, album_id)).fetchone()
