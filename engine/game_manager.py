import pygame
import json
from enum import Enum

class GameState(Enum):
    GAMEPLAY = 1
    DIALOGUE = 2
    INVENTORY = 3

class GameManager:
    def __init__(self, width=1024, height=768):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Melee Prelude v0.1")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.state = GameState.GAMEPLAY
        self.selected_verb = None
        self.inventory = []
        self.scenes = self.load_scenes('data/scenes.json')
        self.current_scene = 'melee_docks'
        self.running = True

    def load_scenes(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            obj = self.get_hotspot_at(event.pos)
            if obj:
                self.interact(self.selected_verb, obj)

    def interact(self, verb, obj):
        scene = self.scenes[self.current_scene]
        interaction = scene['hotspots'][obj].get(verb, {'text': "Nothing happens."})
        self.narrate(interaction['text'])
        if 'add_item' in interaction:
            self.inventory.append(interaction['add_item'])
        if 'exhausted' in interaction:
            scene['hotspots'][obj]['exhausted'] = True  # Grey out next render

    def narrate(self, text):
        surf = self.font.render(text, True, (0, 255, 255))
        self.screen.blit(surf, (50, 700))  # Bottom narration bar

    def get_hotspot_at(self, pos):
        # Placeholder: rect-based hotspot check
        return 'rope_coil' if 200 < pos[0] < 300 and 400 < pos[1] < 500 else None

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.screen.fill((10, 10, 40))  # Dark sea bg
            # Render scene bg, hotspots, verb grid, inventory (placeholders)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

# Usage: manager = GameManager(); manager.run()
