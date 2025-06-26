import pygame
import os
import sys
pygame.init()

# Fenstergröße
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Raumwechsel mit Tür")

# Pfade
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(FILE_PATH, "images")

# Raumgrößen
room_sizes = [
    (900, 900),  # Schlafzimmer
    (900, 450)   # Flur
]

class Room:
    def __init__(self, image_path, size, door_rect, image_folder):
        self.size = size
        self.door_rect = door_rect
        self.image = self.load_and_scale_image(
            os.path.join(image_folder, image_path), size[0], size[1]
        )

    @staticmethod
    def load_and_scale_image(image_path, target_width, target_height):
        image = pygame.image.load(image_path).convert()
        image_width, image_height = image.get_size()
        new_height = int(target_width / image_width * image_height)
        if new_height > target_height:
            new_width = int(image_width * target_height / image_height)
            new_height = target_height
        else:
            new_width = target_width
        return pygame.transform.scale(image, (new_width, new_height))

    def get_offset(self, screen_width, screen_height):
        image_width, image_height = self.image.get_size()
        x_offset = (screen_width - image_width) // 2
        y_offset = (screen_height - image_height) // 2
        return x_offset, y_offset

class Player:
    def __init__(self, start_pos, size=(40, 40), color=(0, 200, 0), speed=5):
        self.rect = pygame.Rect(*start_pos, *size)
        self.color = color
        self.speed = speed

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def draw(self, surface, offset):
        surface_rect = self.rect.move(*offset)
        pygame.draw.rect(surface, self.color, surface_rect)

    def set_position(self, pos):
        self.rect.topleft = pos


class Door(pygame.sprite.Sprite):
    def __init__(self, image_path, position, source_room, target_room, spawn_position):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=position)
        self.source_room = source_room  # NEU!
        self.target_room = target_room
        self.spawn_position = spawn_position




class Game:
    SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Raumwechsel mit Tür")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "playing"  # oder "black", wenn du das sofort testen willst


        self.file_path = os.path.dirname(os.path.abspath(__file__))
        self.image_path = os.path.join(self.file_path, "images")

        # Räume laden
        self.rooms = [
            Room("schlafzimmer.png", (900, 900), None, self.image_path),
            Room("flur.png", (900, 900), None, self.image_path),
            Room("küche.png", (900, 900), None, self.image_path),
            
        ]

        # Türen (als separate Objekte mit Zielraum)
        self.doors = [
            Door(os.path.join(self.image_path, "tür1.png"), (10, 210), source_room=0, target_room=1, spawn_position=(350, 640)),
            Door(os.path.join(self.image_path, "tür1.1.png"), (390, 580), source_room=1, target_room=0, spawn_position=(100, 300)),
            Door(os.path.join(self.image_path, "tür2.png"), (10, 240), source_room=1, target_room=2, spawn_position=(655, 740)),
            Door(os.path.join(self.image_path, "tür1.1.png"), (700, 725), source_room=2, target_room=1, spawn_position=(100, 250)),
            Door(os.path.join(self.image_path, "tür3.png"), (200, 135), source_room=1, target_room=None, spawn_position=(0, 0))

        ]


        self.current_room = 0
        self.player = Player((310, 775))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            print("Spielerposition:", self.player.rect.topleft)

            for door in self.doors:
                if door.source_room == self.current_room:
                    if self.player.rect.colliderect(door.rect):
                        if door.target_room is None:
                            self.state = "black"  # Schwarzer Bildschirm
                        else:
                            self.current_room = door.target_room
                            self.player.set_position(door.spawn_position)
                        break




    def draw(self):
        if self.state == "black":
            self.screen.fill((0, 0, 0))  # Schwarzes Bild
        else:
            self.screen.fill((0, 0, 0))
            room = self.rooms[self.current_room]
            offset = room.get_offset(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            
            
            for door in self.doors:
                if door.source_room == self.current_room:
                    door_screen_rect = door.rect.move(*offset)
                    self.screen.blit(door.image, door_screen_rect)
                    self.screen.blit(room.image, offset)
            self.player.draw(self.screen, offset)
            

    


        #self.screen.blit(room.image, offset)
        #self.player.draw(self.screen, offset)
        pygame.display.flip()


if __name__ == "__main__":
    Game().run()

