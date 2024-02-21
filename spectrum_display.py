import numpy as np
import pygame


class SpectrumDisplay:

    MAX_MAGNITUDE = 300000

    def __init__(self, screen, position, size, num_bins):
        self.screen = screen
        self.position = position
        self.size = size
        self.bin_width = size[0] / num_bins
        self.bin_gap = self.bin_width * 0.2

    def draw_bars(self, magnitudes):
        bar_rects = []

        for i, magnitude in enumerate(magnitudes):
            height = np.clip(magnitude / self.MAX_MAGNITUDE *
                             self.size[1], 0, self.size[1])
            bar_rects.append([i * self.bin_width,
                              0, self.bin_width - self.bin_gap, height])

        bar_rects = np.array(bar_rects)

        # mirroring around the x-axis
        bar_rects[:, 1] = self.size[1] - bar_rects[:, 3]

        # transition to original coordinates
        bar_rects[:, 0] += self.position[0]
        bar_rects[:, 1] += self.position[1]

        # Now draw the rectangles using the transformed coordinates
        for rect in bar_rects:
            pygame.draw.rect(self.screen, (255, 255, 255), rect)
