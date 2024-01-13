import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import pyaudio
import threading
import queue
import time

def open_stream(audio, format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024):
    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)
    return stream

def audio_processing_thread(stream, chunk, q, stop_event):
    while not stop_event.is_set():
        data = stream.read(chunk, exception_on_overflow=False)
        q.put(data)

def analyse_spectrum(data, rate, num_bins, bins):
    frames = np.frombuffer(data, dtype=np.int16)[0::2]
    fft_result = np.fft.fft(frames)
    magnitudes = np.abs(fft_result)

    frequencies = np.fft.fftfreq(len(fft_result), d=1.0/rate)
    indices = np.digitize(frequencies, bins)
    binned_magnitudes = np.zeros(num_bins)

    for i in range(1, len(bins)):
        bin_indices = indices == i
        if np.any(bin_indices):
            binned_magnitudes[i-1] = np.mean(magnitudes[bin_indices])

    return binned_magnitudes

# Main
audio = pyaudio.PyAudio()
stream = open_stream(audio, channels=2, chunk=1024, rate=44100)

# Bin setup
num_bins = 30
min_frequency = 100
max_frequency = 15000
bins = np.logspace(np.log10(min_frequency), np.log10(max_frequency), num_bins + 1)
bin_midpoints = np.sqrt(bins[:-1] * bins[1:])
x = np.arange(num_bins)

# Setup Matplotlib
fig, ax = plt.subplots()
bars = ax.bar(x, np.zeros(num_bins), align='center', edgecolor='black')
ax.set_xticks(x[::5])
ax.set_xticklabels(["{:.0f} Hz".format(freq) for freq in bin_midpoints[::5]])
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Magnitude')
ax.set_title('Binned Magnitudes of Frequencies')
ax.set_ylim(0, 10000)  # Set fixed y-axis range

# Start audio processing thread
audio_queue = queue.Queue()
stop_event = threading.Event()
audio_thread = threading.Thread(target=audio_processing_thread, args=(stream, 1024, audio_queue, stop_event))
audio_thread.start()

try:
    while True:
        while not audio_queue.empty():
            data = audio_queue.get()
            binned_magnitudes = analyse_spectrum(data, 44100, num_bins, bins)
            # for bar, height in zip(bars, binned_magnitudes):
            #     bar.set_height(height)
            # plt.pause(0.001)  # Short pause to update the plot
        time.sleep(0.01)  # Yield execution to allow other processes, including GUI updates
                
except KeyboardInterrupt:
    stop_event.set()
    audio_thread.join()

# Clean up
stream.stop_stream()
stream.close()
audio.terminate()
plt.close(fig)
