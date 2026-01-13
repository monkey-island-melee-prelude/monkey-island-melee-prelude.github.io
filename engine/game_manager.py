import pygame
import json
from enum import Enum

class GameState(Enum):
    GAMEPLAY = 1
    DIALOGUE = 2
    INVENTORY = 3

class UIManager:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.verbs = [
            "GIVE", "OPEN", "CLOSE", "PICK UP", "LOOK AT", "USE",
            "TALK TO", "PUSH", "PULL", "HACK", "Q-ENTANGLE", "BUREAUCRATIZE"
        ]
        self.CYAN = (0, 255, 255)
        self.MAGENTA = (255, 0, 255)
        self.BG = (0, 10, 30)

    def draw_verb_grid(self, mouse_pos, selected_verb):
        for i, verb in enumerate(self.verbs):
            x = 20 + (i % 3) * 110
            y = 580 + (i // 3) * 40
            rect = pygame.Rect(x, y, 100, 30)
            is_hovered = rect.collidepoint(mouse_pos)
            color = self.MAGENTA if is_hovered or verb == selected_verb else self.CYAN
            text_surf = self.font.render(verb, True, color)
            self.screen.blit(text_surf, (x, y))
            if is_hovered:
                glow = text_surf.copy()
                glow.set_alpha(100)
                self.screen.blit(glow, (x+2, y+2))

    def draw_inventory(self, items):
        pygame.draw.rect(self.screen, self.CYAN, (360, 570, 640, 180), 2)
        for i, item in enumerate(items[:6]):  # Limit display
            text_surf = self.font.render(f"[{item}]", True, self.CYAN)
            self.screen.blit(text_surf, (380 + i * 100, 590))

    def apply_glitch(self, intensity=5):
        if intensity > 0:
            for y in range(0, 768, 4):
                offset = (5 if (pygame.time.get_ticks() // 100) % 2 == 0 else -5) * intensity // 10
                pygame.draw.line(self.screen, (0, 255, 255, 50), (offset, y), (1024 + offset, y), 1)

class GameManager:
    def __init__(self, width=1024, height=768):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Melee Prelude v0.2")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.state = GameState.GAMEPLAY
        self.selected_verb = None
        self.inventory = []
        self.game_flags = {}  # e.g., {"crate_moved": True}
        self.narration_queue = []  # ChatGPT rec
        self.scenes = self.load_scenes('data/scenes.json')
        self.hints = self.load_hints('data/hints.json')
        self.current_scene = 'melee_docks'
        self.ui = UIManager(self.screen, self.font)
        self.running = True
        self.glitch_intensity = 0

    def load_scenes(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"melee_docks": {"hotspots": {}}}  # Fallback

    def load_hints(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:  # Hint stub
                self.show_hint()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.state == GameState.GAMEPLAY:
                # Verb selection first
                for i, verb in enumerate(self.ui.verbs):
                    x = 20 + (i % 3) * 110
                    y = 580 + (i // 3) * 40
                    if x <= mouse_pos[0] <= x + 100 and y <= mouse_pos[1] <= y + 30:
                        self.selected_verb = verb
                        self.narrate(f"Selected: {verb}")
                        return
                # Hotspot interact
                obj = self.get_hotspot_at(mouse_pos)
                if obj:
                    self.interact(self.selected_verb or "LOOK AT", obj)

    def get_hotspot_at(self, pos):
        scene = self.scenes.get(self.current_scene, {})
        hotspots = scene.get('hotspots', {})
        for name, hotspot in hotspots.items():
            rect = hotspot.get('rect')
            if rect and len(rect) == 4:
                x1, y1, x2, y2 = rect
                if x1 <= pos[0] <= x2 and y1 <= pos[1] <= y2:
                    if hotspot.get('exhausted'):
                        self.narrate(self.exhausted_text(name))
                        return None
                    if hotspot.get('visible_if') and not self.check_flag(hotspot['visible_if']):
                        return None
                    return name
        return None

    def check_flag(self, flag):
        return self.game_flags.get(flag, False)

    def set_flag(self, flag, value=True):
        self.game_flags[flag] = value

    def interact(self, verb, obj):
        scene = self.scenes[self.current_scene]
        hotspot = scene['hotspots'][obj]
        interaction = hotspot['interactions'].get(verb, {'text': self.exhausted_text(obj)})
        self.narrate(interaction['text'])
        if 'add_item' in interaction:
            self.inventory.append(interaction['add_item'])
            self.glitch_intensity = 10  # Gemini glitch trigger
        if 'exhausted' in interaction:
            hotspot['exhausted'] = True
        if 'state_change' in interaction:
            self.set_flag(interaction['state_change'])
        if 'recruit' in interaction:
            self.narrate(f"Recruited {obj}!")  # Stub

    def exhausted_text(self, obj):
        defaults = {
            "DEFAULT": "Nothing new here.",
            "seagull": "The seagull ignores you now."
        }
        return defaults.get(obj, "I've done that.")

    def show_hint(self):
        hints = self.hints.get(self.current_scene, ["No hints yet."])
        self.narrate(hints[0])  # Escalation stub

    def narrate(self, text):
        self.narration_queue.append(text)
        if len(self.narration_queue) > 3:
            self.narration_queue.pop(0)

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                self.handle_event(event)
            self.screen.fill((10, 10, 40))
            # Render scene bg placeholder
            pygame.draw.rect(self.screen, (20, 20, 60), (0, 0, 1024, 560))  # Sea
            # UI
            self.ui.draw_verb_grid(mouse_pos, self.selected_verb)
            self.ui.draw_inventory(self.inventory)
            self.ui.apply_glitch(self.glitch_intensity)
            self.glitch_intensity = max(0, self.glitch_intensity - 1)
            # Narration queue (ChatGPT)
            for i, text in enumerate(self.narration_queue):
                surf = self.small_font.render(text[:40], True, (0, 255, 255))
                self.screen.blit(surf, (50, 700 - i * 25))
            # Inventory count
            inv_surf = self.font.render(f"Inv: {len(self.inventory)}", True, (0, 255, 255))
            self.screen.blit(inv_surf, (900, 580))
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    manager = GameManager()
    manager.run()
