import pygame
import math
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Zigzag constants
ZIGZAG_AMPLITUDE = 20
ZIGZAG_FREQUENCY = 0.025
TRANSITION_SPEED = 5
BLACK_PAUSE_DURATION = 30  # in frames (~0.5 sec at 60 FPS)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zig-Zag Transition Structured")


class Room:
    def __init__(self, color, text):
        self.color = color
        self.text = text
        self.font = pygame.font.SysFont(None, 36)

    def draw(self):
        screen.fill(self.color)
        rendered_text = self.font.render(self.text, True, BLACK)
        screen.blit(rendered_text, (WIDTH // 2 - rendered_text.get_width() // 2,
                                    HEIGHT // 2 - rendered_text.get_height() // 2))


class Transition:
    def __init__(self):
        self.in_progress = False
        self.progress = 0
        self.complete = False
        self.black_pause_active = False
        self.black_pause_timer = 0

    def start(self):
        self.in_progress = True
        self.complete = False
        self.progress = 0
        self.black_pause_active = False
        self.black_pause_timer = 0

    def update(self):
        if self.in_progress and not self.complete:
            self.progress += TRANSITION_SPEED
            if self.progress >= WIDTH + ZIGZAG_AMPLITUDE * 2:
                self.complete = True
                self.black_pause_active = True
                self.black_pause_timer = BLACK_PAUSE_DURATION
        elif self.black_pause_active:
            self.black_pause_timer -= 1
            if self.black_pause_timer <= 0:
                self.black_pause_active = False
                self.in_progress = False
                self.progress = 0
                return True  # Signal: Raumwechsel jetzt
        return False

    def draw(self):
        if self.black_pause_active:
            screen.fill(BLACK)
        elif self.in_progress:
            wipe_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            points = []
            for y in range(0, HEIGHT + 10, 2):
                x = WIDTH - self.progress + math.sin(y * ZIGZAG_FREQUENCY) * ZIGZAG_AMPLITUDE
                points.append((x, y))
            points.append((WIDTH, HEIGHT))
            points.append((WIDTH, 0))
            if len(points) > 2:
                pygame.draw.polygon(wipe_surface, (0, 0, 0, 255), points)
            screen.blit(wipe_surface, (0, 0))


class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_room_index = 0
        self.rooms = [
            Room(WHITE, "Aktueller Raum – Drücke SPACE"),
            Room((200, 200, 255), "Nächster Raum")
        ]
        self.transition = Transition()

    def run(self):
        while self.running:
            self.handle_events()
            room_switch = self.transition.update()

            if room_switch:
                self.current_room_index = (self.current_room_index + 1) % len(self.rooms)

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.transition.in_progress:
                    self.transition.start()

    def draw(self):
        if self.transition.in_progress or self.transition.black_pause_active:
            self.rooms[self.current_room_index].draw()
            self.transition.draw()
        else:
            self.rooms[self.current_room_index].draw()


# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
