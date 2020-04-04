#!/usr/bin/python3
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

plt.style.use(['dark_background'])

if __name__ == '__main__':

    fig = plt.figure(figsize=(20, 3))
    fig.tight_layout()
    ax = plt.axes()

    spike_limit = 20

    def animate(i):
        try:
            with open('/home/mahmooz/.cache/music_daemon/audio_data.raw', 'rb') as f:
                audio_bytes = f.read()
        except:
            pass

        audio_samples = []
        idx = 0
        while idx < len(audio_bytes):
            audio_sample = int.from_bytes(audio_bytes[idx:idx+2], byteorder='little')
            audio_samples.append(audio_sample)
            idx += 2

        final_samples = []
        idx = 0
        for i in range(spike_limit):
            samples_to_combine = audio_samples[idx:idx+spike_limit]
            if len(samples_to_combine) < spike_limit:
                break
            combined_sample = sum(samples_to_combine) / len(samples_to_combine)
            final_samples.append(combined_sample)
            idx += spike_limit

        X = np.linspace(0, 1, len(final_samples))
        return ax.bar(X, final_samples, align='edge', width=0.05)

    plt.axis('off')
    ax.set_yticks([])
    ax.set_xticks([])

    anim = FuncAnimation(fig, animate, interval=200, blit=True)

    plt.show()
