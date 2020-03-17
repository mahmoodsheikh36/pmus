import pyaudio
import subprocess
import threading
import requests

CHUNK = 1024    # number of bytes to read on each loop
SAMPLE_SIZE = 2 # each sample is 2 bytes
RATE = 44100    # number of frames per second
CHANNELS = 2    # each frame has 2 samples because 2 channels

class MusicPlayer:
    def __init__(self):
        self.song = None
        self.playing = False
        self.stream = None
        self.p = pyaudio.PyAudio()

    def pause(self):
        self.playing = False

    def resume(self):
        self.playing = True

    def seek(self, position_in_seconds):
        self.play(self.current_file, position_in_seconds)

    def play_file(self, path, initial_position=0):
        self.current_file = path
        self.playing = True
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()

        song = subprocess.Popen(["ffmpeg", "-i", path, "-loglevel",
                                "panic", "-vn", "-f", "s16le", "pipe:1"],
                                stdout=subprocess.PIPE)

        self.stream = self.p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                output=True)

        self.stream.start_stream()

        data = song.stdout.read(CHUNK)

        self.progress = 0
        while len(data) > 0:
            if self.playing:
                if self.progress >= initial_position:
                    self.stream.write(data)
                increase_in_progress = len(data) / SAMPLE_SIZE / CHANNELS / RATE
                self.progress = self.progress + increase_in_progress
                print(self.progress)
                data = song.stdout.read(CHUNK)
            else:
                pass

        self.stream.stop_stream()
        self.stream.close()

    def terminate(self):
        self.p.terminate()
