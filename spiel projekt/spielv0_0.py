import pygame
import os
import sys

# Initialisierung
pygame.init()

# Fenstergröße
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Raumwechsel mit Tür")

# Pfade
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(FILE_PATH, "images")

# Raumgrößen
room_sizes = [
    (800, 800),  # Schlafzimmer
    (800, 400)   # Flur
]

# Raumgrafiken laden und skalieren
room_images = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGE_PATH, f"schlafzimmer.png")).convert(),
        room_sizes[0]
    ),
    pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGE_PATH, f"flur.png")).convert(),
        room_sizes[1]
    )
]

# Türen definieren (in Raum-Koordinaten)
door_rects = [
    pygame.Rect(700, 250, 50, 100),  # Tür im Schlafzimmer
    pygame.Rect(50, 150, 50, 100)    # Tür im Flur
]

# Spieler (grünes Rechteck)
player_rect = pygame.Rect(100, 300, 40, 40)
player_speed = 5

# Aktueller Raum
current_room = 0

def draw_player(rect):
    pygame.draw.rect(screen, (0, 200, 0), rect)

def get_room_offset(room_index):
    room_width, room_height = room_sizes[room_index]
    x_offset = (SCREEN_WIDTH - room_width) // 2
    y_offset = (SCREEN_HEIGHT - room_height) // 2
    return x_offset, y_offset

# Spiel-Loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Bewegung
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed
    if keys[pygame.K_UP]:
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN]:
        player_rect.y += player_speed

    # Bildschirm leeren
    screen.fill((0, 0, 0))

    # Aktuellen Raum zeichnen
    x_off, y_off = get_room_offset(current_room)
    screen.blit(room_images[current_room], (x_off, y_off))

    # Tür in aktueller Raum-Position
    door = door_rects[current_room]
    door_screen = door.move(x_off, y_off)
    pygame.draw.rect(screen, (255, 0, 0), door_screen, 2)

    # Spieler zeichnen
    player_screen = player_rect.move(x_off, y_off)
    draw_player(player_screen)

    # Kollision prüfen
    if player_rect.colliderect(door):
        current_room = (current_room + 1) % len(room_images)
        # Neue Startposition des Spielers je nach Raum
        if current_room == 0:
            player_rect.topleft = (100, 300)
        else:
            player_rect.topleft = (SCREEN_WIDTH - 140, 200)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
