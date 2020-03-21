class Song:
    def __init__(self, song_id, name, artists, audio_url, duration, sample_rate,
                 channels, album=None, index_in_album=None):
        self.id = song_id
        self.name = name
        self.artists = artists
        self.audio_url = audio_url
        self.album = album
        self.index_in_album = index_in_album
        self.duration = duration
        self.sample_rate = sample_rate
        self.channels = channels

    def to_map(self, include_artists=True):
        self_map = {}
        self_map['id'] = self.song_id
        self_map['name'] = self.name
        if include_artists:
            self_map['artists'] = [artist.to_map() for artist in self.artists]
        self_map['audio_url'] = self.audio_url
        if self.album is not None:
            self_map['album'] = self.album.to_map()

    def has_album():
        return self.album is not None

    def is_single():
        return self.album is None

class Album:
    def __init__(self, album_id, name, songs, artists, year,
                 image_file_id):
        self.id = album_id
        self.name = name
        self.artists = artists
        self.year = year
        self.image_file_id = image_file_id
        self.songs = songs

class Artist:
    def __init__(self, artist_id, name, albums, singles):
        self.id = artist_id
        self.name = name
        self.albums = albums
        self.singles = singles

class MusicLibrary:
    def __init__(self, songs, artists, albums, singles):
        self.songs = songs
        self.artists = artists
        self.albums = albums
        self.singles = singles

    def get_song(self, song_id):
        for song in self.songs:
            if song.id == song_id:
                return song
        return None

    def get_album(self, album_id):
        for album in self.albums:
            if album.id == album_id:
                return album
        return None
