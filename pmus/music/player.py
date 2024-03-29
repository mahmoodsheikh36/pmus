import pyaudio
import subprocess
import threading
import os
from enum import Enum

from pmus.music.music import Track
from pmus.utils.utils import current_time, file_exists
from pmus.db.db import DBProvider
from pmus.utils.config import config_on_play

SAMPLE_SIZE = 2 # each sample is 2 bytes (-f s16le with ffmpeg)

class MusicPlayerMode(Enum):
    LOOP_TRACK = 1
    LOOP_QUEUE = 2

class AudioTask():
    def __init__(self):
        self.running = True
        self.pyaudio = pyaudio.PyAudio()

    def terminate(self):
        self.running = False

    def run(self, url, initial_position, on_progress_increase, on_complete):
        # idk why but some audio files at 96k become distorted, temporary fix
        sample_rate = 96000
        channels = 2
        ffmpeg_stream = subprocess.Popen(["ffmpeg", "-ss", str(initial_position),
                                 "-i", url, "-loglevel", "panic", "-vn",
                                 "-f", "s16le", "-acodec", "pcm_s16le", "-ar",
                                  str(sample_rate), "-ac", str(channels),
                                  "pipe:1"],
                                  stdout=subprocess.PIPE)

        audio_stream = self.pyaudio.open(format=pyaudio.paInt16,
                                         channels=channels,
                                         rate=sample_rate,
                                         output=True)

        bytes_to_read = 1024
        audio_bytes = ffmpeg_stream.stdout.read(bytes_to_read)
        progress = 0
        while audio_bytes:
            audio_stream.write(audio_bytes)
            increase_in_progress =\
                bytes_to_read / SAMPLE_SIZE / channels / sample_rate
            progress = progress + increase_in_progress
            if self.running:
                on_progress_increase(increase_in_progress)
            else:
                break
            audio_bytes = ffmpeg_stream.stdout.read(bytes_to_read)

        # cleanup
        ffmpeg_stream.terminate()
        ffmpeg_stream.kill()
        audio_stream.stop_stream()
        audio_stream.close()

        if self.running:
            on_complete()

class MusicPlayer:
    def __init__(self):
        self.track_queue = []
        self.ended_track_queue = []
        self.audio_task = None
        self.audio_task_thread = None
        self.music_monitor = MusicMonitor(self, DBProvider())
        self.progress = None
        self.playing = False
        self.mode = MusicPlayerMode.LOOP_QUEUE

    def play_album(self, album):
        self.track_queue.clear()
        self.ended_track_queue.clear()
        self.play(album.tracks[0])
        for track in album.tracks[1:]:
            self.add_to_queue(track)

    def play_clear_queue(self, track):
        self.track_queue.clear()
        self.ended_track_queue.clear()
        self.play(track)

    def play(self, track, initial_progress=0):
        if not file_exists(track.audio_file_path):
            return
        if self.mode == MusicPlayerMode.LOOP_TRACK:
            self.mode = MusicPlayerMode.LOOP_QUEUE
        if self.track_queue:
            self.ended_track_queue.append(self.track_queue.pop())
        self.track_queue.append(track)
        self.play_url(track.audio_file_path, initial_progress)
        self.playing = True
        self.music_monitor.on_play()
        config_on_play(self.current_track())

    def add_to_queue(self, track):
        was_empty = not self.track_queue
        self.track_queue.insert(0, track)
        if was_empty:
            self.play_url(track.audio_file_path)
            self.playing = True
            self.music_monitor.on_play()
            config_on_play(self.current_track())

    def clear_queue(self):
        current_track = self.current_track()
        self.track_queue.clear()
        self.ended_track_queue.clear()
        self.track_queue.append(current_track)

    def pause(self):
        if not self.playing:
            return
        self.terminate_audio_task()
        self.music_monitor.on_pause()
        self.playing = False

    def resume(self):
        if self.playing or self.current_track() is None:
            return
        track = self.current_track()
        self.play_url(track.audio_file_path, self.progress)
        self.playing = True
        self.music_monitor.on_resume()

    def seek(self, position_in_seconds):
        if not self.current_track():
            return
        self.play_url(self.current_track().audio_file_path, position_in_seconds)
        self.music_monitor.on_seek()

    def play_url(self, url, initial_position=0):
        self.progress = initial_position
        self.start_audio_task(url, initial_position)

    def start_audio_task(self, url, initial_position):
        self.terminate_audio_task()
        self.audio_task = AudioTask()
        t = threading.Thread(target = self.audio_task.run,
                             args = (url, initial_position,
                                     self.on_audio_task_progress,
                                     self.on_track_complete))
        t.start()
        self.audio_task_thread = t

    def on_audio_task_progress(self, increase_in_progress):
        self.progress += increase_in_progress

    def terminate_audio_task(self):
        if self.audio_task:
            self.audio_task.terminate()
            """
            if we arent terminating from main thread then we are terminating
            from the same thread that called this function and therefore
            calling audio_task_thread.join() would throw an error
            so we only call join() when terminating from main thread
            """
            if threading.current_thread() is threading.main_thread():
                self.audio_task_thread.join()

    def terminate(self):
        print('terminating player')
        self.terminate_audio_task()
        self.music_monitor.terminate()

    def on_track_complete(self):
        if self.mode == MusicPlayerMode.LOOP_TRACK:
            self.play_url(self.track_queue[-1].audio_file_path)
            self.music_monitor.on_skip()
            config_on_play(self.current_track())
        elif self.mode == MusicPlayerMode.LOOP_QUEUE:
            self.skip_to_next()

    def skip_to_next(self):
        if not self.track_queue:
            return
        if self.mode == MusicPlayerMode.LOOP_TRACK:
            self.mode = MusicPlayerMode.LOOP_QUEUE
        self.ended_track_queue.insert(0, self.track_queue.pop())
        if not self.track_queue:
            self.track_queue.append(self.ended_track_queue.pop())
        self.play_url(self.track_queue[-1].audio_file_path)
        self.playing = True
        self.music_monitor.on_skip()
        config_on_play(self.current_track())

    def skip_to_prev(self):
        if not self.track_queue:
            return
        if self.progress > 5:
            self.play_url(self.track_queue[-1].audio_file_path)
            self.playing = True
            self.music_monitor.on_seek()
        else:
            if not self.ended_track_queue:
                if not self.track_queue:
                    return
                track_to_play = self.track_queue.pop(0)
                if self.track_queue: # if track_to_play wasnt the only track in queue
                    self.ended_track_queue.insert(0, self.track_queue.pop())
            else:
                track_to_play = self.ended_track_queue[0]
                self.ended_track_queue[0] = self.track_queue.pop()
            if self.mode == MusicPlayerMode.LOOP_TRACK:
                self.mode = MusicPlayerMode.LOOP_QUEUE
            self.track_queue.append(track_to_play)
            self.play_url(self.track_queue[-1].audio_file_path)
            self.playing = True
            self.music_monitor.on_skip()
            config_on_play(self.current_track())

    def current_track(self):
        if self.track_queue:
            return self.track_queue[-1]
        return None

    def current_tracks(self):
        return self.track_queue + self.ended_track_queue

class MusicMonitor:
    def __init__(self, music_player, db_provider):
        self.music_player = music_player
        self.db_provider = db_provider
        self.playback = None

    def on_play(self):
        track_id = self.music_player.current_track().id
        now = current_time()
        self.update_current_playback_time_ended(now)
        playback_time_started = now
        playback_time_ended = -1
        playback_id = self.db_provider.add_playback(playback_time_started,
                                                    playback_time_ended,
                                                    track_id)
        self.playback = {'time_started': playback_time_started,
                         'time_ended': playback_time_ended,
                         'id': playback_id}

    def update_current_playback_time_ended(self, time_ended):
        if self.playback:
            self.db_provider.update_playback_time_ended(self.playback['id'],
                                                        time_ended)

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
