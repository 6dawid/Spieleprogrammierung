import pygame
import os
import sys
from time import sleep

# Fenstergröße (erstmal noch die alten Werte)
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nächtlicher Hungers Albtraum - Dawid Rzepka")

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
        self.state = "menu"  # Starte im Menü statt "playing"

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

        # Menü-Setup - Schöne Schriftarten
        try:
            self.menu_font_title = pygame.font.SysFont("Times New Roman", 58)  # Elegant
            self.menu_font_button = pygame.font.SysFont("Calibri", 32)  # Modern
        except:
            # Fallback falls Schriftarten nicht verfügbar
            self.menu_font_title = pygame.font.SysFont("Arial", 60)
            self.menu_font_button = pygame.font.SysFont("Arial", 36)
        
        # Start-Button (Rechteck für Maus-Kollision)
        self.start_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 60)

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
        
        # Telefon-System (nach Kommode)
        self.handy_available = False  # Wird True nachdem Kommode benutzt wurde
        self.show_phone_menu = False
        self.show_phone_call_result = False
        self.current_phone_call = None  # "polizei", "mutter", "freund", "unbekannt"
        
        # Tracking für Aktionen (für dynamische Gespräche)
        self.has_checked_window = False
        self.has_checked_kühlschrank = False
        
        # Tracking für bereits angerufene Personen
        self.called_persons = {
            "polizei": False,
            "mutter": False,
            "freund": False,
            "unbekannt": False
        }

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

    def draw_phone_message(self, lines):
        # Zeichne Telefon-Text auf schwarzem Hintergrund (spezielle Version für Telefon)
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 25)
        text = font.render("Drücke ENTER für Weiter", True, (180, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH // 2 - 100, 20))
        y = 200
        for line in lines:
            # Bestimme Farbe basierend auf Sprecher
            if line.startswith("Polizei:") or line.startswith("Mutter:") or line.startswith("Freund:") or line.startswith("Unbekannt:"):
                # Andere Person spricht
                color = (255, 100, 100)  # Rot für andere Personen
            elif line.startswith("Du:") or line.startswith("Du ") or "Du legst" in line:
                # Spieler spricht oder handelt
                color = (100, 255, 100)  # Grün für Spieler
            else:
                # Beschreibungstext
                color = (255, 255, 255)  # Weiß für Beschreibungen
            
            text_surface = font.render(line, True, color)
            self.screen.blit(text_surface, (50, y))
            y += 30

    def draw_menu(self):
        # Zeichne Hauptmenü
        self.screen.fill((20, 20, 40))  # Dunkler Hintergrund
        
        # Spiel-Titel
        title_text = self.menu_font_title.render("Nächtlicher Hungers Albtraum ", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))  # Weiter nach oben
        self.screen.blit(title_text, title_rect)
        
        # Untertitel
        subtitle_text = self.menu_font_button.render("Erstellt von Dawid Rzepka", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))  # Mehr Abstand
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Start-Button
        mouse_pos = pygame.mouse.get_pos()
        button_color = (100, 200, 100) if self.start_button.collidepoint(mouse_pos) else (60, 120, 60)
        text_color = (255, 255, 255) if self.start_button.collidepoint(mouse_pos) else (200, 200, 200)
        
        pygame.draw.rect(self.screen, button_color, self.start_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.start_button, 3)
        
        start_text = self.menu_font_button.render("START", True, text_color)
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_rect)


        




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

            # Menü-Events (Mausklick)
            elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "menu":
                if event.button == 1:  # Linke Maustaste
                    if self.start_button.collidepoint(event.pos):
                        self.state = "playing"  # Starte das Spiel
                        print("Spiel gestartet!")
                else:
                    pass

            elif event.type == pygame.KEYDOWN and self.state == "playing":
                # ESC: Doppelklick zum Beenden (nur im Spiel)
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
                        self.state = "the_end"  # Gehe zu THE END Bildschirm
                        self.current_fragment_index = 0  # Reset für nächstes Mal
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
                
                # H: Telefon benutzen (nur wenn Handy verfügbar)
                if event.key == pygame.K_h and self.handy_available and not self.show_phone_menu:
                    self.show_phone_menu = True

                if self.show_window_choice:
                    if event.key == pygame.K_1:
                        self.show_window_choice = False
                        self.show_window_result = True
                        self.has_checked_window = True  # Merke, dass Fenster gecheckt wurde
                    elif event.key == pygame.K_2:
                        self.show_window_choice = False

                elif self.show_window_result and event.key == pygame.K_RETURN:
                    self.show_window_result = False

                if self.show_kül_choice:
                    if event.key == pygame.K_1:
                        self.show_kül_choice = False
                        self.show_kül_result = True
                        self.has_checked_kühlschrank = True  # Merke, dass Kühlschrank gecheckt wurde
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
                        self.handy_available = True  # Handy ist jetzt verfügbar
                    elif event.key == pygame.K_2:
                        self.show_komode_choice = False
                
                elif self.show_komode_result and event.key == pygame.K_RETURN:
                    self.show_komode_result = False

                # Telefon-Menü Navigation
                if self.show_phone_menu:
                    if event.key == pygame.K_1 and not self.called_persons["polizei"]:  # Polizei
                        self.show_phone_menu = False
                        self.show_phone_call_result = True
                        self.current_phone_call = "polizei"
                    elif event.key == pygame.K_2 and not self.called_persons["mutter"]:  # Mutter
                        self.show_phone_menu = False
                        self.show_phone_call_result = True
                        self.current_phone_call = "mutter"
                    elif event.key == pygame.K_3 and not self.called_persons["freund"]:  # Freund
                        self.show_phone_menu = False
                        self.show_phone_call_result = True
                        self.current_phone_call = "freund"
                    elif event.key == pygame.K_4 and not self.called_persons["unbekannt"]:  # Unbekannte Nummer
                        self.show_phone_menu = False
                        self.show_phone_call_result = True
                        self.current_phone_call = "unbekannt"
                    elif event.key == pygame.K_5:  # Abbrechen
                        self.show_phone_menu = False

                elif self.show_phone_call_result and event.key == pygame.K_RETURN:
                    # Markiere Person als angerufen bevor das Gespräch beendet wird
                    if self.current_phone_call:
                        self.called_persons[self.current_phone_call] = True
                    self.show_phone_call_result = False
                    self.current_phone_call = None

            # THE END Bildschirm Events
            elif event.type == pygame.KEYDOWN and self.state == "the_end":
                if event.key == pygame.K_SPACE:
                    self.state = "menu"  # Zurück zum Hauptmenü
                    # Spiel zurücksetzen für neues Spiel
                    self.current_room = 0
                    self.player.set_position((280, 750))
                    self.komode_used = False
                    self.current_fragment_index = 0
                    # Alle Interaktions-Zustände zurücksetzen
                    self.show_window_choice = False
                    self.show_window_result = False
                    self.show_kül_choice = False
                    self.show_kül_result = False
                    self.show_bett_choice = False
                    self.show_bett_result = False
                    self.show_komode_choice = False
                    self.show_komode_result = False
                    # Telefon-System zurücksetzen
                    self.handy_available = False
                    self.show_phone_menu = False
                    self.show_phone_call_result = False
                    self.current_phone_call = None
                    # Aktions-Tracking zurücksetzen
                    self.has_checked_window = False
                    self.has_checked_kühlschrank = False
                    # Telefon-Tracking zurücksetzen (alle Personen wieder anrufbar)
                    self.called_persons = {
                        "polizei": False,
                        "mutter": False,
                        "freund": False,
                        "unbekannt": False
                    }


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
        # Nur Spiel-Logik wenn im Spiel-Zustand
        if self.state == "menu":
            pass  # Menü braucht keine Updates
        elif (self.state == "playing" and 
            not self.show_window_choice and not self.show_window_result and
            not self.show_kül_choice and not self.show_kül_result and
            not self.show_bett_choice and not self.show_bett_result and
            not self.show_komode_choice and not self.show_komode_result and
            not self.show_phone_menu and not self.show_phone_call_result):
            
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
        # Zeichne je nach Zustand
        if self.state == "menu":
            self.draw_menu()  # Zeichne Hauptmenü
        elif self.state == "the_end":
            self.draw_the_end()  # Zeichne THE END Bildschirm
        elif self.state == "black":
            self.screen.fill((0, 0, 0))  # Schwarzes Ende
        elif self.state == "playing":
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

            #pygame.draw.rect(self.screen, (255, 0, 0), self.komode_rect.move(*offset), 2) if self.current_room == 1 else None   # Debug
             
            # Zeige "Drücke E" wenn bei interaktivem Objekt
            if self.player_is_near_window() or self.player_is_near_kül() or self.player_is_near_bett() or (self.player_is_near_komode() and not self.komode_used):
                font = pygame.font.SysFont(None, 35)
                text = font.render("Drücke E", True, (180, 255, 255))
                self.screen.blit(text, (SCREEN_WIDTH // 2 - 100, 20))
            
            # Zeige "Drücke H" wenn Handy verfügbar
            if self.handy_available and not self.show_phone_menu and not self.show_phone_call_result:
                font = pygame.font.SysFont(None, 30)
                text = font.render("Drücke H zum Telefonieren", True, (255, 255, 150))
                self.screen.blit(text, (SCREEN_WIDTH // 2 - 120, 60))
             
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

            # === TELEFON-SYSTEM ===
            if self.show_phone_menu:
                self.draw_phone_menu()
            
            if self.show_phone_call_result:
                self.screen.fill((0, 0, 0))
                call_text = self.get_phone_call_text(self.current_phone_call)
                self.draw_phone_message(call_text)


                

        # Aktualisiere Bildschirm
        pygame.display.flip()

    def draw_the_end(self):
        # Zeichne THE END Bildschirm
        self.screen.fill((0, 0, 0))  # Schwarzer Hintergrund
        
        # THE END Titel - groß und dramatisch
        try:
            end_font = pygame.font.SysFont("Times New Roman", 80)
            subtitle_font = pygame.font.SysFont("Arial", 32)
        except:
            end_font = pygame.font.SysFont("Arial", 80)
            subtitle_font = pygame.font.SysFont("Arial", 32)
        
        # THE END Text
        end_text = end_font.render("THE END", True, (255, 50, 50))
        end_rect = end_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(end_text, end_rect)
        
        # Untertitel
        thanks_text = subtitle_font.render("Danke fürs Spielen!", True, (200, 200, 200))
        thanks_rect = thanks_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(thanks_text, thanks_rect)
        
        # Anweisung zurück zum Menü
        instruction_text = subtitle_font.render("Drücke SPACE für Hauptmenü", True, (150, 150, 255))
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        self.screen.blit(instruction_text, instruction_rect)

    def get_phone_call_text(self, call_type):
        # Verschiedene Telefongespräche
        if call_type == "mutter":
            return self.get_mutter_conversation()  # Verwende dynamisches Gespräch
        elif call_type == "polizei":
            return self.get_polizei_conversation()  # Verwende dynamisches Gespräch
        elif call_type == "freund":
            return self.get_freund_conversation()  # Verwende dynamisches Gespräch
        elif call_type == "unbekannt":
            return self.get_unbekannt_conversation()  # Verwende dynamisches Gespräch
        elif call_type == "unbekannt":
            return self.get_unbekannt_conversation()  # Neues mysteriöses Gespräch
        
        phone_calls = {}
        return phone_calls.get(call_type, ["Kein Text verfügbar."])

    def get_mutter_conversation(self):
        # Dynamisches Mutter-Gespräch basierend auf Aktionen
        base_conversation = [
            "Du wählst Mutters Nummer. Das Freizeichen...",
            "Mutter: 'Hallo?'",
            "Du: 'Ich bin's, ich kann nicht schlafen.'",
            "Mutter: 'Schatz? Wie spät ist es?'",
            "Du: 'Spät… habe ich dich geweckt?'",
            "Mutter: 'Ja… ist wieder etwas passiert?'"
        ]
        
        # Je nach Aktionen verschiedene Fortsetzungen
        if self.has_checked_kühlschrank and self.has_checked_window:
            # Option C: Beides getan
            continuation = [
                "Du: 'Im Kühlschrank ist nur eine riesige tote Fliege … und da steht jemand vor meinem Haus …'",
                "Mutter: 'Was?! Eine tote Fliege im Kühlschrank? Und jemand vor dem Haus?'",
                "Mutter: 'Das klingt ja wie ein Horrorfilm!'",
                "Du: 'Ich weiß nicht, was ich tun soll …'",
                "Mutter: 'Ruf die Polizei an!'",
                "*PIEPTON* - Die Verbindung bricht ab."
            ]
        elif self.has_checked_kühlschrank:
            # Option A: Nur Kühlschrank
            continuation = [
                "Du: 'Im Kühlschrank ist nur eine riesige tote Fliege …'",
                "Mutter: 'Was? Eine tote Fliege? Wie kommt die da rein?'",
                "Du: 'Keine Ahnung, aber es ist echt eklig. Ich hab nichts zu essen.'",
                "Mutter: 'Dann hol dir was vom Imbiss oder bestell dir was.'",
                "Mutter: 'Ich lege jetzt auf, ich will deinen Vater nicht wecken.'",
                "Du: 'Ja… gute Nacht.'"
            ]
        elif self.has_checked_window:
            # Option B: Nur Fenster
            continuation = [
                "Du: 'Da steht jemand vor meinem Haus …'",
                "Mutter: 'Was? Wer steht da? Das ist ja gruselig!'",
                "Du: 'Ich weiß nicht, aber der schaut direkt zu mir hoch …'",
                "Mutter: 'Ruf die Polizei an!'",
                "*PIEPTON* - Die Verbindung bricht ab."
            ]
        else:
            # Option D: Nichts getan
            continuation = [
                "Du: 'Nein, ich hab nur Hunger.'",
                "Mutter: 'Dann hol dir einen Snack und geh wieder ins Bett.'",
                "Mutter: 'Wenn es nichts Ernstes ist, lege ich jetzt auf.'",
                "Mutter: 'Ich will deinen Vater nicht wecken.'",
                "Du: 'Ja… gute Nacht.'"
            ]
        
        return base_conversation + continuation

    def get_polizei_conversation(self):
        # Dynamisches Polizei-Gespräch basierend auf Aktionen - realistisch und kurz
        base_conversation = [
            "Du wählst 110. Es klingelt...",
            "Polizei: 'Polizeinotruf, was ist Ihr Notfall?'"
        ]
        
        # Je nach Aktionen verschiedene Gespräche
        if self.has_checked_window:
            # Option A: Fenster geschaut
            continuation = [
                "Du: 'Da steht jemand vor meinem Haus!'",
                "Polizei: 'Können Sie die Person beschreiben?'",
                "Du: 'Nur einen Schatten... aber die Person schaut zu mir hoch!'",
                "Polizei: 'Einen Schatten? Sind Sie sicher, dass da jemand ist?'",
                "Du: 'Ja, ganz sicher!'",
                "Polizei: 'Wir haben keine Streife frei für unklare Schatten.'",
                "*TUUT TUUT* - Sie haben aufgelegt."
            ]
        else:
            # Option B: Nichts Besonderes getan - nur Hunger
            continuation = [
                "Du: 'Ähm, ja, ich hab ein Problem... ich bin hungrig.'",
                "Polizei: 'Hungrig? Das ist kein Notfall.'",
                "Du: 'Aber die Lieferdienste haben alle geschlossen!'",
                "Polizei: 'Wir sind hier für echte Notfälle. Nicht für Hungerattacken.'",
                "*TUUT TUUT* - Sie haben aufgelegt."
            ]
        
        return base_conversation + continuation

    def get_freund_conversation(self):
        # Dynamisches Freund-Gespräch basierend auf Aktionen - sarkastisch und müde
        base_conversation = [
            "Du rufst deinen besten Freund an.",
            "Freund: 'Ugh… was willst du? Es ist mitten in der Nacht…'",
            "Du: 'Ich kann nicht schlafen.'",
            "Freund: 'Wow. Unglaublich. Echt der Wahnsinn. Das passiert nachts manchmal.'",
            "Du: 'Aber ich hab auch Hunger …'",
            "Freund: 'Dann iss was und lass mich schlafen.'"
        ]
        
        # Je nach Aktionen verschiedene Fortsetzungen
        if self.has_checked_kühlschrank and self.has_checked_window:
            # Option D: Beides getan
            continuation = [
                "Du: 'Im Kühlschrank war nur eine riesige tote Fliege …'",
                "Freund: 'Lecker. Guten Appetit.'",
                "Du: 'Nicht witzig! Und draußen steht jemand vor meinem Haus …'",
                "Freund: 'Perfekt! Lad ihn doch ein und teilt euch die Fliege.'",
                "Du: 'Ich hasse dich.'",
                "Freund: 'Gute Nacht.'",
                "*TUUT TUUT* - Er hat aufgelegt."
            ]
        elif self.has_checked_kühlschrank:
            # Option A: Nur Kühlschrank
            continuation = [
                "Du: 'Im Kühlschrank war nur eine riesige tote Fliege …'",
                "Freund: 'Lecker. Guten Appetit.'",
                "Du: 'Nicht witzig!'",
                "Freund: 'Komm schon, Protein ist wichtig.'",
                "Du: 'Ich hasse dich.'",
                "Freund: 'Gute Nacht.'",
                "*TUUT TUUT* - Er hat aufgelegt."
            ]
        elif self.has_checked_window:
            # Option B: Nur Fenster
            continuation = [
                "Du: 'Aber da steht jemand vor meinem Haus …'",
                "Freund: 'Cool. Frag ihn, ob er Pizza dabei hat.'",
                "Du: 'Ich mein das ernst!'",
                "Freund: 'Dann ruf die Polizei an. Und lass mich schlafen.'",
                "Du: 'Ich hasse dich.'",
                "Freund: 'Gute Nacht.'",
                "*TUUT TUUT* - Er hat aufgelegt."
            ]
        else:
            # Option C: Nichts getan
            continuation = [
                "Du: 'Ja, okay…'",
                "Freund: 'Gute Nacht.'",
                "*TUUT TUUT* - Er hat aufgelegt."
            ]
        
        return base_conversation + continuation

    def get_unbekannt_conversation(self):
        # Mysteriöses Gespräch mit unbekannter Nummer
        return [
            "Eine fremde Nummer. Du wählst sie.",
            "Es klingelt lange. Dann:",
            "Unbekannt: 'Hast du es gefunden?'",
            "Du: 'Was? Meinen Kühlschrank? Da war nur eine tote Fliege …'",
            "Unbekannt: 'Achso? Oh, dann habe ich wohl die falsche Nummer erwischt. Tut mir leid!'",
            "*TUUT TUUT* - Die Person legt hastig auf.",
            "Du starrst verwirrt auf das Handy. Was solltest du gefunden haben?"
        ]

    def draw_phone_menu(self):
        # Zeichne Telefonmenü mit Status der bereits angerufenen Personen
        font = pygame.font.SysFont(None, 32)
        box = pygame.Rect(50, 800, 900, 150)
        pygame.draw.rect(self.screen, (30, 30, 30), box)
        pygame.draw.rect(self.screen, (255, 255, 255), box, 2)

        # Telefonmenü-Optionen mit Status
        phone_options = [
            ("1: Polizei (110)", "polizei"),
            ("2: Mutter", "mutter"), 
            ("3: Freund", "freund"),
            ("4: Unbekannte Nummer", "unbekannt"),
            ("5: Abbrechen", None)
        ]

        for i, (option_text, person_key) in enumerate(phone_options):
            # Bestimme Farbe basierend auf Status
            if person_key and self.called_persons[person_key]:
                # Bereits angerufen - ausgegraut
                color = (100, 100, 100)
                display_text = option_text + " (bereits angerufen)"
            elif person_key is None:
                # Abbrechen-Option - normal
                color = (255, 255, 255)
                display_text = option_text
            else:
                # Noch nicht angerufen - normal
                color = (255, 255, 255)
                display_text = option_text

            text = font.render(display_text, True, color)
            self.screen.blit(text, (60, 810 + i * 30))

# Spiel starten
if __name__ == "__main__":
    Game().run()
