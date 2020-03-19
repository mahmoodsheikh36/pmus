import pyaudio
import subprocess
import threading
import requests
from music import Song

CHUNK = 1024    # number of bytes to read on each iteration
SAMPLE_SIZE = 2 # each sample is 2 bytes
RATE = 44100    # number of frames per second
CHANNELS = 2    # each frame has 2 samples because 2 channels

class AudioTask():
    def __init__(self, url):
        self.running = True

    def terminate():
        self.running = False

    def run(self, pyaudio_instance, url, on_progress, on_complete):
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

        self.progress = 0
        while self.running and len(data) > 0:
            stream.write(data)
            increase_in_progress = len(data) / SAMPLE_SIZE / CHANNELS / RATE
            self.progress = self.progress + increase_in_progress
            print(self.progress)
            data = ffmpeg_stream.stdout.read(CHUNK)

        print('done playing audio {}'.format(url))
        stream.stop_stream()
        stream.close()
        on_complete()

class MusicPlayer:
    def __init__(self):
        self.playing = False
        self.song_queue = []
        self.ended_song_queue = []
        self.p = pyaudio.PyAudio()
        self.audio_task = None
        self.audio_task_thread = None

    def play(self, song):
        if self.song_queue:
            self.ended_song_queue.append(self.song_queue.pop())
        self.song_queue.append(song)
        self.playing = True
        self.play_url(song.audio_url)

    def add_to_queue(self, song):
        self.song_queue.insert(0, song)
        """
        maybe we should start playing if the player is not already playing
        and if the queue was empty before adding the song to the queue?
        maybe not? maybe the user just wants to organize the queue and then
        tell the player to start playing
        """

    def clear_queue(self):
        self.song_queue.clear()
        self.ended_song_queue.clear()

    def pause(self):
        self.playing = False

    def resume(self):
        self.playing = True

    def seek(self, position_in_seconds):
        self.play_file(self.song.audio_url, position_in_seconds)

    def play_url(self, url, initial_position=0):
        self.start_audio_task(url, initial_position)
        self.progress = 0
        self.playing = True

    def start_audio_task(url, initial_position):
        if self.audio_task:
            self.audio_task.terminate()
            self.audio_task_thread.join()

        self.audio_task = AudioTask()
        t = Thread(target = self.audio_task.run,
                   args = (self.p, url,
                           lambda progress: self.progress = progress,
                           self.on_song_complete))
        t.start()
        self.audio_task_thread = t

    def terminate(self):
        self.p.terminate()
        if self.audio_task:
            self.audio_task.terminate()
            self.audio_task_thread.join()

    def on_song_complete(self):
        self.ended_song_queue.insert(0, self.song_queue.pop())
        if not self.song_queue:
            self.song_queue.append(self.ended_song_queue.pop())
        self.play_url(self.song_queue[-1].audio_url)
