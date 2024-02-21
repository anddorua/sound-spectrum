import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import pyaudio
import pygame
import threading
import queue
import time

from spectrum_display import SpectrumDisplay

SPECTRUM_HEIGHT = 600
NUM_BINS = 80

pygame.init()
screen = pygame.display.set_mode((800, SPECTRUM_HEIGHT))

spectrum_left = SpectrumDisplay(screen, (0, 0), (800, SPECTRUM_HEIGHT), NUM_BINS)
# spectrum_right = SpectrumDisplay(screen, (400, 0), (400, SPECTRUM_HEIGHT), NUM_BINS)

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

def analyse_spectrum(frames, rate, num_bins, bins):
    fft_result = fft(frames)
    magnitudes = np.abs(fft_result)

    frequencies = fftfreq(len(fft_result), d=1.0/rate)
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
min_frequency = 100
max_frequency = 15000
bins = np.logspace(np.log10(min_frequency), np.log10(max_frequency), NUM_BINS + 1)
print(bins)
bin_midpoints = np.sqrt(bins[:-1] * bins[1:])
print(bin_midpoints)

# Start audio processing thread
audio_queue = queue.Queue()
stop_event = threading.Event()
audio_thread = threading.Thread(target=audio_processing_thread, args=(stream, 1024, audio_queue, stop_event))
audio_thread.start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    while not audio_queue.empty():
        data = audio_queue.get()
        all_frames = np.frombuffer(data, dtype=np.int16)
        binned_magnitudes_left = analyse_spectrum(all_frames[0::2], 48000, NUM_BINS, bins)
        # binned_magnitudes_right = analyse_spectrum(all_frames[1::2], 44100, NUM_BINS, bins)
        
        screen.fill((0, 0, 0))
        spectrum_left.draw_bars(binned_magnitudes_left)
        # spectrum_right.draw_bars(binned_magnitudes_right)
        pygame.display.flip()
    time.sleep(0.01)  # Yield execution to allow other processes, including GUI updates


print('Stopping...')         
stop_event.set()
audio_thread.join()

# Clean up
stream.stop_stream()
stream.close()
audio.terminate()
