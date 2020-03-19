import pyaudio
import subprocess
import threading

from music import Song
from utils import current_time
from db import DBProvider

CHUNK = 1024    # number of bytes to read on each iteration
SAMPLE_SIZE = 2 # each sample is 2 bytes
RATE = 44100    # number of frames per second
CHANNELS = 2    # each frame has 2 samples because 2 channels

class AudioTask():
    def __init__(self):
        self.running = True

    def terminate(self):
        self.running = False

    def run(self, pyaudio_instance, url, initial_position,
            on_progress, on_complete):
        ffmpeg_stream = subprocess.Popen(["ffmpeg", "-ss", str(initial_position),
                                 "-i", url, "-loglevel",
                                 "panic", "-vn", "-f", "s16le", "pipe:1"],
                                  stdout=subprocess.PIPE)

        stream = pyaudio_instance.open(format=pyaudio.paInt16,
                                       channels=CHANNELS,
                                       rate=RATE,
                                       output=True)

        stream.start_stream()

        data = ffmpeg_stream.stdout.read(CHUNK)

        progress = 0
        while self.running and len(data) > 0:
            stream.write(data)
            increase_in_progress = len(data) / SAMPLE_SIZE / CHANNELS / RATE
            progress = progress + increase_in_progress
            on_progress(progress)
            data = ffmpeg_stream.stdout.read(CHUNK)

        stream.stop_stream()
        stream.close()
        ffmpeg_stream.terminate()
        if self.running:
            on_complete()

class MusicPlayer:
    def __init__(self):
        self.playing = False
        self.song_queue = []
        self.ended_song_queue = []
        self.audio_task = None
        self.audio_task_thread = None
        self.pyaudio_instance = pyaudio.PyAudio()
        self.music_monitor = MusicMonitor(self, DBProvider())

    def play(self, song):
        if self.song_queue:
            self.ended_song_queue.append(self.song_queue.pop())
        self.song_queue.append(song)
        self.playing = True
        self.play_url(song.audio_url)
        self.music_monitor.on_play()

    def add_to_queue(self, song):
        self.song_queue.insert(0, song)
        """
        maybe we should start playing if the player is not already playing
        and if the queue was empty before adding the song to the queue?
        maybe not? maybe the user just wants to organize the queue and then
        tell the player to start playing
        """

    def clear_queue(self):
        current_song = self.current_song()
        self.song_queue.clear()
        self.ended_song_queue.clear()
        self.song_queue.append(current_song)

    def pause(self):
        self.playing = False
        self.music_monitor.on_pause()

    def resume(self):
        self.playing = True
        self.music_monitor.on_resume()

    def seek(self, position_in_seconds):
        self.play_file(self.song.audio_url, position_in_seconds)
        self.music_monitor.on_seek()

    def play_url(self, url, initial_position=0):
        self.start_audio_task(url, initial_position)
        self.progress = 0
        self.playing = True

    def start_audio_task(self, url, initial_position):
        if self.audio_task:
            self.audio_task.terminate()
            self.audio_task_thread.join()

        self.audio_task = AudioTask()
        t = threading.Thread(target = self.audio_task.run,
                             args = (self.pyaudio_instance, url,
                                     initial_position,
                                     self.on_audio_task_progress,
                                     self.on_song_complete))
        t.start()
        self.audio_task_thread = t

    def on_audio_task_progress(self, progress):
        self.progress = progress
        print(self.progress)

    def terminate(self):
        if self.audio_task:
            self.audio_task.terminate()
            self.audio_task_thread.join()
        self.pyaudio_instance.terminate()
        self.music_monitor.terminate()

    def on_song_complete(self):
        self.skipToNext()

    def skipToNext(self):
        self.ended_song_queue.insert(0, self.song_queue.pop())
        if not self.song_queue:
            self.song_queue.append(self.ended_song_queue.pop())
        self.play_url(self.song_queue[-1].audio_url)
        self.music_monitor.on_skip()

    def current_song(self):
        if self.song_queue:
            return self.song_queue[-1]
        return None

class MusicMonitor:
    def __init__(self, music_player, db_provider):
        self.music_player = music_player
        self.db_provider = db_provider
        self.playback = None

    def on_play(self):
        song_id = self.music_player.current_song().id
        now = current_time()
        self.update_current_playback_time_ended(now)
        playback_time_started = now
        playback_time_ended = -1
        playback_id = self.db_provider.add_playback(playback_time_started,
                                                    playback_time_ended,
                                                    song_id)
        self.playback = {'time_started': playback_time_started,
                         'time_ended': playback_time_ended,
                         'id': playback_id}

    def update_current_playback_time_ended(self, time_ended):
        if self.playback:
            self.db_provider.update_playback_time_ended(self.playback['id'],
                                                        time_ended)
            self.db_provider.commit()

    def terminate(self):
        self.update_current_playback_time_ended(current_time())

    def on_skip(self):
        self.on_play()

    def on_pause(self):
        self.db_provider.add_pause(current_time(), self.playback['id'])

    def on_resume(self):
        self.db_provider.add_resume(current_time(), self.playback['id'])

    def on_seek(self):
        self.db_provider.add_seek(current_time(),
                                  self.music_player.progress,
                                  self.playback['id'])
