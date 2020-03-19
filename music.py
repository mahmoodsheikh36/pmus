class Song:
    def __init__(self, song_id, name, artists, audio_url,
                 album=None, index_in_album=None):
        self.id = song_id
        self.name = name
        self.artists = artists
        self.audio_url = audio_url
        self.album = album
        self.index_in_album = index_in_album

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
