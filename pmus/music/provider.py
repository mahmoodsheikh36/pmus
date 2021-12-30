import os
import os.path

from pmus.db.db import DBProvider
from pmus.utils.config import config
from pmus.music.ffmpeg import get_audio_format
from pmus.utils.utils import file_exists
from pmus.music.music import Artist, Track, Album, Playback

AUDIO_FILE_EXTENSIONS = ['mp3', 'flac', 'opus', 'm4a']

class MusicProvider:
    def __init__(self):
        self.db_provider = DBProvider()
        self.tracks = {}
        self.albums = {}
        self.singles = {}
        self.artists = {}
        self.playbacks = {}

    def unload_music(self):
        self.tracks = {}
        self.albums = {}
        self.singles = {}
        self.artists = {}
        self.playbacks = {}

    def load_music(self):
        db_tracks = self.db_provider.get_tracks()
        db_artists = self.db_provider.get_artists()
        db_albums = self.db_provider.get_albums()
        db_track_artists = self.db_provider.get_track_artists()
        db_album_artists = self.db_provider.get_album_artists()
        db_playbacks = self.db_provider.get_playbacks()
        db_pauses = self.db_provider.get_pauses()
        db_resumes = self.db_provider.get_resumes()

        for db_artist in db_artists:
            artist = Artist(db_artist['id'], db_artist['name'], [], [])
            self.artists[artist.id] = artist

        for db_album in db_albums:
            album = Album(db_album['id'], db_album['name'], [],
                          [], db_album['year'])
            self.albums[album.id] = album

        for db_track in db_tracks:
            track = Track(db_track['id'], album, db_track['audio_file_path'], db_track['name'],
                          [], db_track['duration'], playbacks=[])
            self.tracks[track.id] = track
            album.tracks.append(track)

        for db_album_artist in db_album_artists:
            album_id = db_album_artist['album_id']
            artist_id = db_album_artist['artist_id']
            self.artists[artist_id].albums.append(self.albums[album_id])
            self.albums[album_id].artists.append(self.artists[artist_id])

        for db_track_artist in db_track_artists:
            track_id = db_track_artist['track_id']
            artist_id = db_track_artist['artist_id']
            self.tracks[track_id].artists.append(self.artists[artist_id])

        # remove tracks/albums that were deleted/moved from filesystem
        for album in list(self.albums.values()):
            for track in list(album.tracks):
                if not file_exists(track.audio_file_path):
                    album.tracks.remove(track)
                    del self.tracks[track.id]
            if not album.tracks:
                del self.albums[album.id]

        # sort tracks in album by their index in it
        #for album in self.albums.values():
        #    for i in range(len(album.tracks)):
        #        for j in range(i + 1, len(album.tracks)):
        #            if album.tracks[j].index_in_album < album.tracks[i].index_in_album:
        #                album.tracks[i], album.tracks[j] = album.tracks[j], album.tracks[i]

        for db_playback in db_playbacks:
            playback = Playback(db_playback['id'],
                                db_playback['track_id'],
                                db_playback['time_started'],
                                db_playback['time_ended'],
                                [], [])
            self.playbacks[db_playback['id']] = playback
            if db_playback['track_id'] in self.tracks:
                self.tracks[db_playback['track_id']].playbacks.append(playback)

        for db_pause in db_pauses:
            self.playbacks[db_pause['playback_id']].pauses.append(db_pause)

        for db_resume in db_resumes:
            self.playbacks[db_resume['playback_id']].pauses.append(db_resume)

    def on_audio_file_found(self, filepath):
        for track in self.tracks.values():
            if track.audio_file_path == filepath:
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
        track_name = tags['title']

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
                old_track = self.db_provider.get_track_by_album(album_id, idx_in_album)
                if old_track is not None:
                    if file_exists(old_track['audio_file_path']):
                        return
            track_id = self.db_provider.add_track(track_name, album_id, filepath,
                                                  audio_format['duration'], idx_in_album)
            for db_artist in db_artists:
                self.db_provider.add_track_artist(track_id, db_artist['id'])

    def find_music(self, music_dir=config.music_dir):
        for folder, subs, files in os.walk(music_dir):
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

    def get_tracks_list(self):
        return list(self.tracks.values())

    def get_albums_list(self):
        return list(self.albums.values())

    def get_artists_list(self):
        return list(self.artists.values())
    
    def get_playbacks_list(self):
        return list(self.playbacks.values())
