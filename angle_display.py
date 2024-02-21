import pygame;
import math;

class AngleDisplay:
    def __init__(self, screen, position, size):
        self.screen = screen
        self.position = position
        self.size = size

    # Draw the angle
    # angle: -90 to 90 degrees
    # left_sector: the additional sector to the left from the angle, shows possible lef deviation
    # right_sector: the additional sector to the right from the angle, shows possible right deviation
    def draw_angle(self, angle, left_sector, right_sector):
        # Draw the angle
      
        start_angle = (270 + angle - left_sector) / 180.0 * math.pi;
        stop_angle = (270 + angle + right_sector) / 180.0 * math.pi;
        pygame.draw.arc(self.screen, 
                        (255, 255, 143), 
                        (self.size[0]*0.1, self.size[1]*0.1, self.size[0]*0.8, self.size[1]*0.8), 
                        start_angle, 
                        stop_angle, width =  int(self.size[0]*0.4))
        pygame.draw.line(self.screen, (255, 255, 255), (0, self.size[1]/2), (self.size[0], self.size[1]/2), 2)
        center_line_length = self.size[0]*0.4
        center_line_x = math.sin(angle / 180.0 * math.pi) * center_line_length
        center_line_y = math.cos(angle / 180.0 * math.pi) * center_line_length
        pygame.draw.line(self.screen, 
                         (0, 0, 255), 
                         (self.size[0]/2-1, self.size[1]/2), 
                         (self.size[0]/2-1 + center_line_x, self.size[1]/2 + center_line_y), 
                         2)
        # Draw the center
        pygame.draw.circle(self.screen, (255, 0, 0), (self.size[0]/2, self.size[1]/2), 6, 0)

        # Render the angle value
        font = pygame.font.Font(None, 72)
        text = font.render("{:.0f}".format(angle), True, (255, 255, 255))
        text_rect = text.get_rect()
        self.screen.blit(text, 
                         ((self.size[0] - text_rect[2])*0.5, self.size[1]/4 - text_rect[3]/2))
