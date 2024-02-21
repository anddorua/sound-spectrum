# This application uses stereo microphone input to determine the direction of a sound source.
#
# The application uses the following steps:
# 1. Open a stereo audio stream.
# 2. Start a thread that reads the chunks of audio data from the stream and puts it into a queue.
# 3. In the main loop, the application reads the audio data from the queue and processes it.
# 4. Each chunk of audio data is filtered to leave the band range about 1000 Hz
# 5. Channel chunks get correlated to find the time delay between the channels.
# 6. The time delay is converted to an angle and displayed on the screen.

import pygame
import time
import pyaudio
import numpy as np
import math
from scipy.signal import firwin2, lfilter
from microphone_sound_provider import MicrophoneSoundProvider
from angle_display import AngleDisplay;

DISPLAY_SIZE = (600, 600)
FS=44100 # sample rate
N_SAMPLES=1024 # number of samples per chunk
FB = 2730 # target frequency
MIC_BASE = 0.0625 # distance between microphones, meters
SOUND_SPEED = 343.0 # speed of sound, meters/second
MAX_DELAY = MIC_BASE/SOUND_SPEED # maximum delay between channels
MAX_DELAY_IN_SAMPLES = math.ceil(FS * MAX_DELAY) # maximum delay in samples

print(f"Max delay in samples: {MAX_DELAY_IN_SAMPLES}")

# Create running window to calculate 
angle_running_window_length = int((FS * 0.5) / N_SAMPLES)
angle_running_window = np.zeros(angle_running_window_length)
angle_running_window_index = 0

# Filter calculation
lst_freqs = np.linspace(0, FS/2, 100)
target_freqs = np.logical_not(np.logical_or(lst_freqs < FB-FS/2/100, lst_freqs > FB+FS/2/100))
lst_gain = np.select([np.logical_not(target_freqs), target_freqs], [np.zeros(len(target_freqs)), np.ones(len(target_freqs))])
NFIR = 64
taps = firwin2(NFIR, lst_freqs, lst_gain, fs=FS)

# Init direction display
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)
angle_display = AngleDisplay(screen, (100, 100), DISPLAY_SIZE)

sound_provider = MicrophoneSoundProvider(pyaudio.paInt16, 2, FS, N_SAMPLES)

queue = sound_provider.openStream()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    while not queue.empty():
        data = queue.get()
        samples = np.frombuffer(data, dtype=np.int16)
        left_cahnnel_samples = samples[::2]
        right_channel_samples = samples[1::2]
        
        # Apply filter
        left_cahnnel_samples = lfilter(taps, 1.0, left_cahnnel_samples)
        right_channel_samples = lfilter(taps, 1.0, right_channel_samples)

        # Pad with zeros for all range of possible delays
        left_cahnnel_samples = np.pad(left_cahnnel_samples, 
                                      (MAX_DELAY_IN_SAMPLES, MAX_DELAY_IN_SAMPLES), 
                                      constant_values=(0, 0))
        
        # Calculate correlation
        corr = np.correlate(left_cahnnel_samples, right_channel_samples, mode='valid')

        # Find the index of max correlation
        max_corr_index = np.argmax(corr)
        
        # Find the angle
        delay = (max_corr_index - MAX_DELAY_IN_SAMPLES)/FS
        angle = math.degrees(math.asin(np.clip(delay*SOUND_SPEED/MIC_BASE, -1., 1.)))

        if (angle_running_window_index == angle_running_window_length):
            angle_running_window_index = 0
        angle_running_window[angle_running_window_index] = angle
        angle_running_window_index += 1

        angle_var = np.var(angle_running_window)
        angle_mean = np.mean(angle_running_window)
        
        print(f"Angle: {angle_mean}, Var: {angle_var}")

        screen.fill((0, 0, 0))
        angle_display.draw_angle(angle_mean, 10, 10)
        pygame.display.flip()
    time.sleep(0.01)  # Yield execution to allow other processes, including GUI updates

sound_provider.closeStream()
pygame.quit()