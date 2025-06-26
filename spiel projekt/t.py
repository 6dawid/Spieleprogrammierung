import pygame
import os
import sys
from time import sleep

# Fenstergröße (erstmal noch die alten Werte)
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Raumwechsel mit Tür")

# Pfade (behalten für Kompatibilität)
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(FILE_PATH, "images")


class Room:
    def __init__(self, image_path, size, door_rect, image_folder):
        self.size = size
        self.door_rect = door_rect
        # Lade und skaliere das Raumbild
        self.image = self.load_and_scale_image(
            os.path.join(image_folder, image_path), size[0], size[1]
        )

    @staticmethod
    def load_and_scale_image(image_path, target_width, target_height):
        # Lade Bild und berechne Skalierung
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
        # Zentriere das Bild
        image_width, image_height = self.image.get_size()
        x_offset = (screen_width - image_width) // 2
        y_offset = (screen_height - image_height) // 2
        return x_offset, y_offset


class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, speed):
        super().__init__()
        # Lade Spielerbild
        self.image = pygame.image.load(os.path.join(IMAGE_PATH, "player.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (70, 100))
        self.rect = self.image.get_rect(topleft=start_pos)
        self.speed = speed

    def move(self, keys):
        # Bewege Spieler mit Pfeiltasten
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def set_position(self, pos):
        # Setze Position für Raumwechsel
        self.rect.topleft = pos


class Door(pygame.sprite.Sprite):
    def __init__(self, image_path, position, source_room, target_room, spawn_position):
        super().__init__()
        # Lade Türbild
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=position)
        self.source_room = source_room  # Von welchem Raum
        self.target_room = target_room  # Zu welchem Raum
        self.spawn_position = spawn_position  # Wo Spieler spawnt



class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Raumwechsel mit Tür")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "playing"

        # Story-Fragmente für Bett-Interaktion
        self.story_bett_fragments = [
            ["Du legst dich ins Bett schließt die Augen. Der Hunger ist noch da, aber irgendwie... unwichtig.",
             "Die Matratze fühlt sich fremd an. Die Dunkelheit hinter deinen Lidern ist zu dick, zu schwer.",
             "Du zählst Schäfchen. Doch jedes, das über den Zaun springt, hat die Flügel einer Fliege",
             "Irgendwann – nach Minuten oder Stunden – versinkst du doch in Schlaf.",
             "Aber es fühlt sich nicht wie Erholung an. Es fühlt sich wie Fallen."],
            ["Du öffnest die Augen. Oder träumst, dass du es tust. Der Raum ist dunkel, aber der Gestank","ist neu: Süßlich-faul. Etwas kriecht über deine Hand. Du möchtest schreien,"," aber dein Mund ist staubtrocken. Dann ist wieder alles weg"],
            ["Irgendwo klingelt ein Telefon. Deins? Es hört nicht auf...."],
            ["Es dauert einen Monat, bis jemand etwas merkt.","Bis die Nachbarin sich beschwert, dass es aus Wohnung 4 'wie modrige Milch mit Tod' stinkt.","Bis der Vermieter mehrmals klopft – und schließlich die Polizei ruft."],
            ["Sie treten ein","Die Hitze schlägt ihnen entgegen.","Im Flur: ein Handy. Akku leer."],
            ["Dann finden sie dich.","Nicht im Bett, sondern halb auf dem Boden, als wärst du aufgestanden","und einfach stecken geblieben.","Deine Haut ist papierdünn, deine Augen halb offen.","Über dir: ein Schwarm Fliegen, summend wie ein kaputter Kühlschrank."],
            ["'Verdammt', flüstert einer der Beamten. 'Das muss Wochen her sein.'","Die Nachbarin weint. 'Er war so still... Ich dachte, er wäre verreist.'"," ","Niemand weiß, warum du vergessen hast zu essen.","Warum du nicht um Hilfe gerufen hast."],
            ["Aber als sie deine Wohnung versiegeln, bleibt eine letzte Fliege an der Scheibe kleben.","Ihre Flügel zittern.","Dann ist alles still."]
        ]

        self.current_fragment_index = 0
        self.running = True

        # ESC-Doppelklick System
        self.esc_pressed = False
        self.esc_timer = 0 

        self.file_path = FILE_PATH
        self.image_path = IMAGE_PATH

        # Lade Interaktionsbilder
        self.window_image = pygame.image.load(os.path.join(self.image_path, "fenster.png"))
        self.window_image = pygame.transform.scale(self.window_image, (600, 600))

        self.kül_image = pygame.image.load(os.path.join(self.image_path, "küchef.png"))
        self.kül_image = pygame.transform.scale(self.kül_image, (600, 600))

        self.komode_image = pygame.image.load(os.path.join(self.image_path, "kommode.png"))
        self.komode_image = pygame.transform.scale(self.komode_image, (600, 600))
        self.komodel_image = pygame.image.load(os.path.join(self.image_path, "kommodel.png"))
        self.komodel_image = pygame.transform.scale(self.komodel_image, (600, 600))

        # Interaktions-Zustände
        self.show_window_choice = False
        self.show_window_result = False

        self.show_kül_choice = False
        self.show_kül_result = False

        self.show_bett_choice = False
        self.show_bett_result = False

        self.komode_used = False
        self.show_komode_choice = False
        self.show_komode_result = False

        # Erstelle Räume
        self.rooms = [
            Room("schlafzimmer.png", (900, 900), None, self.image_path),  # Raum 0
            Room("flur.png", (900, 900), None, self.image_path),          # Raum 1  
            Room("küche.png", (900, 900), None, self.image_path),         # Raum 2
        ]

        # Erstelle Türen
        self.doors = [
            Door(os.path.join(self.image_path, "tür1.png"), (10, 210), source_room=0, target_room=1, spawn_position=(310, 600)),
            Door(os.path.join(self.image_path, "tür1.1.png"), (390, 580), source_room=1, target_room=0, spawn_position=(70, 250)),
            Door(os.path.join(self.image_path, "tür2.png"), (10, 240), source_room=1, target_room=2, spawn_position=(630, 740)),
            Door(os.path.join(self.image_path, "tür1.1.png"), (700, 725), source_room=2, target_room=1, spawn_position=(80, 250)),
            Door(os.path.join(self.image_path, "tür3.png"), (185, 70), source_room=1, target_room=None, spawn_position=(0, 0))  # Ausgang
        ]

        # Kollisions-Rechtecke für Interaktionen
        self.window_rect = pygame.Rect(780, 540, 100, -250)
        self.kül_rect = pygame.Rect(125, 193, 70, 90)
        self.bett_rect = pygame.Rect(340, 630, 220, 270)
        self.komode_rect = pygame.Rect(60, 795, 300, 100)

        # Spieler-Setup
        self.current_room = 0
        self.player = Player((280, 750), speed=5)  # Test mit 5
        self.all_sprites = pygame.sprite.Group(self.player)

    def draw_box(self, options):
        # Zeichne Textbox am unteren Rand
        font = pygame.font.SysFont(None, 32)
        box = pygame.Rect(50, 800, 900, 150)
        pygame.draw.rect(self.screen, (30, 30, 30), box)
        pygame.draw.rect(self.screen, (255, 255, 255), box, 2)

        for i, options in enumerate(options):
            text = font.render(options, True, (255, 255, 255))
            self.screen.blit(text, (60, 810 + i * 30))

    def draw_message(self, lines):
        # Zeichne Story-Text auf schwarzem Hintergrund
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 25)
        text = font.render("Drücke SPACE für Weiter", True, (180, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH // 2 - 100, 20))
        y = 200
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (50, y))
            y += 30


        




    def run(self):
        # Haupt-Spielschleife
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        pygame.quit()
        sys.exit()

    def handle_events(self):
        # Verarbeite alle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # ESC: Doppelklick zum Beenden
                if event.key == pygame.K_ESCAPE:
                    now = pygame.time.get_ticks()
                    if not self.esc_pressed or now - self.esc_timer > 1000:
                        self.esc_pressed = True
                        self.esc_timer = now
                        print("Drücke ESC erneut zum Beenden")
                    else:
                        self.running = False
                else:
                    self.esc_pressed = False

                # SPACE: Navigiere durch Story
                if event.key == pygame.K_SPACE:
                    self.current_fragment_index += 1
                    if self.current_fragment_index >= len(self.story_bett_fragments):
                        self.current_fragment_index = 0
                    else:
                         pass

                # E: Starte Interaktionen
                if event.key == pygame.K_e:
                    if self.player_is_near_window() and not self.show_window_choice:
                        self.show_window_choice = True
                    elif self.player_is_near_kül() and not self.show_kül_choice:
                        self.show_kül_choice = True
                    elif self.player_is_near_bett() and not self.show_bett_choice:
                        self.show_bett_choice = True
                    elif self.player_is_near_komode() and not self.show_komode_choice and not self.komode_used:
                        self.show_komode_choice = True
                    else:
                        pass

                if self.show_window_choice:
                    if event.key == pygame.K_1:
                        self.show_window_choice = False
                        self.show_window_result = True
                    elif event.key == pygame.K_2:
                        self.show_window_choice = False

                elif self.show_window_result and event.key == pygame.K_RETURN:
                    self.show_window_result = False

                if self.show_kül_choice:
                    if event.key == pygame.K_1:
                        self.show_kül_choice = False
                        self.show_kül_result = True
                    elif event.key == pygame.K_2:
                        self.show_kül_choice = False

                elif self.show_kül_result and event.key == pygame.K_RETURN:
                    self.show_kül_result = False

                if self.show_bett_choice:
                    if event.key == pygame.K_1:
                        self.show_bett_choice = False
                        self.show_bett_result = True
                    elif event.key == pygame.K_2:
                        self.show_bett_choice = False
                
                if self.show_komode_choice:
                    if event.key == pygame.K_1:
                        self.show_komode_choice = False
                        self.show_komode_result = True
                        self.komode_used = True
                    elif event.key == pygame.K_2:
                        self.show_komode_choice = False
                
                elif self.show_komode_result and event.key == pygame.K_RETURN:
                    self.show_komode_result = False


    # Kollisions-Prüfungen
    def player_is_near_window(self):
        return self.current_room == 0 and self.player.rect.colliderect(self.window_rect)

    def player_is_near_kül(self):
        return self.current_room == 2 and self.player.rect.colliderect(self.kül_rect)
    
    def player_is_near_bett(self):
        return self.current_room == 0 and self.player.rect.colliderect(self.bett_rect)

    def player_is_near_komode(self):
        return self.current_room == 1 and self.player.rect.colliderect(self.komode_rect)

    def update(self):
        # Spieler-Bewegung und Raumwechsel
        if (self.state == "playing" and 
            not self.show_window_choice and not self.show_window_result and
            not self.show_kül_choice and not self.show_kül_result and
            not self.show_bett_choice and not self.show_bett_result and
            not self.show_komode_choice and not self.show_komode_result):
            
            keys = pygame.key.get_pressed()
            self.player.move(keys)

            # Prüfe Tür-Kollisionen für Raumwechsel
            for door in self.doors:
                if door.source_room == self.current_room:
                    if self.player.rect.colliderect(door.rect):
                        if door.target_room is None:
                            self.state = "black"  # Spiel-Ende
                        else:
                            self.current_room = door.target_room
                            self.player.set_position(door.spawn_position)
                        break

    def draw(self):
        # Zeichne alles auf den Bildschirm
        if self.state == "black":
            self.screen.fill((0, 0, 0))  # Schwarzes Ende
        else:
            # Normaler Spielzustand
            self.screen.fill((0, 0, 0))
            room = self.rooms[self.current_room]
            offset = room.get_offset(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.screen.blit(room.image, offset)
            #pygame.draw.rect(self.screen, (255, 0, 0), self.window_rect.move(*offset), 2) if self.current_room == 0 else None  # Debug
            
            # Zeichne Türen
            for door in self.doors:
                if door.source_room == self.current_room:
                    self.screen.blit(door.image, door.rect.move(*offset))

            # Zeichne Raum nochmal (überlagert Türen)
            self.screen.blit(room.image, offset)
            
            # Zeichne Spieler
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, (sprite.rect.x + offset[0], sprite.rect.y + offset[1]))

            #pygame.draw.rect(self.screen, (255, 0, 0), self.komode_rect.move(*offset), 2) if self.current_room == 1 else None  # Debug
             
            # Zeige "Drücke E" wenn bei interaktivem Objekt
            if self.player_is_near_window() or self.player_is_near_kül() or self.player_is_near_bett() or (self.player_is_near_komode() and not self.komode_used):
                font = pygame.font.SysFont(None, 35)
                text = font.render("Drücke E", True, (180, 255, 255))
                self.screen.blit(text, (SCREEN_WIDTH // 2 - 100, 20))
             
            # Zeige ESC-Anweisung
            if self.esc_pressed:
                font = pygame.font.SysFont(None, 30)
                text = font.render("Nochmal ESC zum Beenden", True, (180, 255, 255))
                self.screen.blit(text, (SCREEN_WIDTH // 2 - 100, 20))

            # === INTERAKTIONS-MENÜS ===
            if self.show_window_choice:
                self.draw_box(["1: Aus dem Fenster schauen", "2: Ignorieren"])

            if self.show_window_result:
                self.screen.fill((0, 0, 0))
                self.screen.blit(self.window_image, (200, 200))
                self.draw_box(["Draußen steht jemand ...",
                "Drücke ENTER, um wegzusehen..."])

            if self.show_kül_choice:
                self.draw_box(["1: Kühlschrank öffnen", "2: Zurücktreten"])
            
            if self.show_kül_result:
                self.screen.fill((0, 0, 0))
                self.screen.blit(self.kül_image, (200, 200))
                self.draw_box(["Eine riesige tote Fliege liegt im Kühlschrank bahhhh XD ... ", 
                "Drücke ENTER, um wegzusehen..."])

            if self.show_bett_choice:
                self.draw_box(["1: Ins Bett legen", "2: Zurücktreten"])

            if self.show_bett_result:
                self.screen.fill((0, 0, 0))
                self.draw_message(self.story_bett_fragments[self.current_fragment_index])



            if self.show_komode_choice:
                self.draw_box(["1: Schublade öffnen", "2: Zurücktreten"])

            if self.show_komode_result:
                current_time = pygame.time.get_ticks()

                if not hasattr(self, "komode_start_time"):
                    self.komode_start_time = current_time

                self.screen.fill((0, 0, 0))

                if current_time - self.komode_start_time < 2000:  # 2000 ms = 2 Sekunde Pause
                    # Zeige erstes Bild und Text
                    self.screen.blit(self.komode_image, (200, 200))
                    self.draw_box(["Du öffnest die Schublade und findest dort ein Handy, das du mitnimmst es..."])
                else:
                    # Zeige zweites Bild und Text
                    self.screen.blit(self.komodel_image, (200, 200))
                    self.draw_box(["Du hast glück das Handy hat 20% noch ...",
                                    "Drücke ENTER, um die Kommode zu schließen..."])


                

        # Aktualisiere Bildschirm
        pygame.display.flip()

# Spiel starten
if __name__ == "__main__":
    Game().run()
