class Playback:
    def __init__(self, playback_id, song_id, time_started, time_ended,
                 pauses=None, resumes=None):
        self.song_id = song_id
        self.time_started = time_started
        self.time_ended = time_ended
        self.pauses = pauses
        self.resumes = resumes
        self.id = playback_id

    def time_listened(self, from_time=None, to_time=None):
        if self.time_ended == -1:
            return 0
        if abs(len(self.pauses) - len(self.resumes)) > 1:
            return 0
        if from_time is None:
            from_time = self.time_started
        elif from_time > self.time_ended:
            return 0
        if to_time is None:
            to_time = self.time_ended
        elif to_time < self.time_started:
            return 0
        if from_time < self.time_started:
            from_time = self.time_started
        if to_time > self.time_ended:
            to_time = self.time_ended
        milliseconds = to_time - from_time
        for i in range(len(self.resumes)):
            pause = self.pauses[i]
            resume = self.resumes[i]
            time_paused = pause['time']
            time_resumed = resume['time']
            if time_paused > to_time:
                continue
            if time_resumed < from_time:
                continue
            if time_paused < from_time:
                time_paused = from_time
            if time_resumed > to_time:
                time_resumed = to_time
            milliseconds -= time_resumed - time_paused
        if len(self.pauses) > len(self.resumes):
            time_paused = self.pauses[-1]['time']
            if time_paused < to_time:
                if time_paused < from_time:
                    time_paused = from_time
                milliseconds -= to_time - time_paused
        return milliseconds

class Song:
    def __init__(self, song_id, audio_url, name, artists, duration,
                 time_liked=None, playbacks=None,
                 album=None, index_in_album=None):
        self.id = song_id
        self.name = name
        self.artists = artists
        self.audio_url = audio_url
        self.album = album
        self.index_in_album = index_in_album
        self.duration = duration
        self.time_liked = time_liked
        self.playbacks = playbacks

    def to_map(self, include_artists=True):
        self_map = {}
        self_map['id'] = self.song_id
        self_map['name'] = self.name
        if include_artists:
            self_map['artists'] = [artist.to_map() for artist in self.artists]
        self_map['audio_url'] = self.audio_url
        if self.album is not None:
            self_map['album'] = self.album.to_map()

    def has_album(self):
        return self.album is not None

    def is_single(self):
        return self.album is None

    def is_liked(self):
        return self.time_liked is not None

    def time_listened(self, from_time=None, to_time=None):
        total = 0
        for playback in self.playbacks:
            total += playback.time_listened(from_time, to_time)
        return total

class Album:
    def __init__(self, album_id, name, songs, artists, year):
        self.id = album_id
        self.name = name
        self.artists = artists
        self.year = year
        self.songs = songs

    def time_listened(self, from_time=None, to_time=None):
        total = 0
        for song in self.songs:
            total += song.time_listened(from_time, to_time)
        return total

class Artist:
    def __init__(self, artist_id, name, albums, singles):
        self.id = artist_id
        self.name = name
        self.albums = albums
        self.singles = singles

    def time_listened(self, from_time=None, to_time=None):
        total = 0
        for album in self.albums:
            total += album.time_listened(from_time, to_time)
        for single in self.singles:
            total += single.time_listened(from_time, to_time)
        return total
