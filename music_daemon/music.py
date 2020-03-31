class Song:
    def __init__(self, song_id, audio_url, name, artists, duration,
                 is_liked=False, seconds_listened=0,
                 album=None, index_in_album=None):
        self.id = song_id
        self.name = name
        self.artists = artists
        self.audio_url = audio_url
        self.album = album
        self.index_in_album = index_in_album
        self.duration = duration
        self.seconds_listened = seconds_listened
        self.is_liked = is_liked

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
    def __init__(self, album_id, name, songs, artists, year):
        self.id = album_id
        self.name = name
        self.artists = artists
        self.year = year
        self.songs = songs

    def seconds_listened(self):
        total_seconds = 0
        for song in self.songs:
            total_seconds += song.seconds_listened
        return total_seconds

class Artist:
    def __init__(self, artist_id, name, albums, singles):
        self.id = artist_id
        self.name = name
        self.albums = albums
        self.singles = singles

    def seconds_listened(self):
        total_seconds = 0
        for album in self.albums:
            total_seconds += album.seconds_listened()
        for single in self.singles:
            total_seconds += single.seconds_listened
        return total_seconds
