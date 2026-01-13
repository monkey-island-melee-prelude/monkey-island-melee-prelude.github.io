# engine/game_manager.py (v0.3.3 - Full merged version with all updates)

import pygame
import json
import math  # For sin/cos in animations
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
        self.verb_rects = []
        self._build_verb_rects()

    def _build_verb_rects(self):
        self.verb_rects = []
        for i, verb in enumerate(self.verbs):
            x = 20 + (i % 3) * 110
            y = 580 + (i // 3) * 40
            self.verb_rects.append((pygame.Rect(x, y, 100, 30), verb))

    def get_verb_at(self, pos):
        """Returns the verb string if clicked, else None."""
        for rect, verb in self.verb_rects:
            if rect.collidepoint(pos):
                return verb
        return None

    def draw_verb_grid(self, mouse_pos, selected_verb):
        for rect, verb in self.verb_rects:
            is_hovered = rect.collidepoint(mouse_pos)
            color = self.MAGENTA if is_hovered or verb == selected_verb else self.CYAN
            text_surf = self.font.render(verb, True, color)
            self.screen.blit(text_surf, (rect.x, rect.y))
            if is_hovered:
                glow = text_surf.copy()
                glow.set_alpha(100)
                self.screen.blit(glow, (rect.x + 2, rect.y + 2))

    def draw_inventory(self, items):
        pygame.draw.rect(self.screen, self.CYAN, (360, 570, 640, 180), 2)
        for i, item in enumerate(items[:6]):
            text_surf = self.font.render(f"[{item.upper()}]", True, self.CYAN)
            self.screen.blit(text_surf, (380 + i * 100, 590))

    def apply_glitch(self, intensity):
        if intensity > 0:
            for y in range(0, 768, 4):
                offset = (5 if (pygame.time.get_ticks() // 100) % 2 == 0 else -5) * intensity // 10
                pygame.draw.line(self.screen, (0, 255, 255, 50), (offset, y), (1024 + offset, y), 1)

class GameManager:
    def __init__(self, width=1024, height=768):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Melee Prelude v0.3.3")
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
        self.dialogues = self.load_dialogues('data/dialogues.json')
        self.items = self.load_items('data/items.json')
        self.current_scene = 'melee_docks'
        self.ui = UIManager(self.screen, self.font)
        self.running = True
        self.glitch_intensity = 0
        self.inventory_flash_time = 0
        self.room_title_time = pygame.time.get_ticks()  # Initial title
        self.combine_anim_time = 0
        self.combine_pos = (0, 0)
        self.cursor_history = []
        self.debug_mode = True
        pygame.mouse.set_visible(False)  # Hide default cursor

    def load_scenes(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"melee_docks": {"hotspots": {}}}

    def load_hints(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def load_dialogues(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def load_items(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                self.show_hint()
            if event.key == pygame.K_f1:
                self.debug_mode = not self.debug_mode
            if event.key == pygame.K_n:  # Stub next scene for testing
                self.change_scene('scumm_bar')  # Cycle for demo
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.state == GameState.GAMEPLAY:
                clicked_verb = self.ui.get_verb_at(mouse_pos)
                if clicked_verb:
                    self.selected_verb = clicked_verb
                    self.narrate(f"Selected: {clicked_verb}")
                    return
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
        if not self.check_conditions(interaction):
            self.narrate("Not yet ready for that.")
            return
        self.narrate(interaction['text'])
        if 'add_item' in interaction:
            self.inventory.append(interaction['add_item'])
            self.inventory_flash_time = pygame.time.get_ticks()
            self.glitch_intensity = 15
            self.trigger_combine_effect()
        if 'exhausted' in interaction:
            hotspot['exhausted'] = True
        if 'state_change' in interaction:
            self.set_flag(interaction['state_change'])
        if 'recruit' in interaction:
            self.narrate(f"Recruited {obj}!")  # Stub
        if 'dialogue_tree' in interaction:
            self.run_dialogue(interaction['dialogue_tree'])

    def check_conditions(self, interaction):
        req = interaction.get('requires')
        if req:
            if isinstance(req, list):
                for item in req:
                    if item not in self.inventory:
                        return False
            else:
                if req not in self.inventory:
                    return False
        req_state = interaction.get('requires_state')
        if req_state and not self.game_flags.get(req_state, False):
            return False
        expr = interaction.get('requires_expr')
        if expr:
            try:
                context = dict(self.game_flags)
                if not eval(expr, {}, context):
                    return False
            except Exception:
                return False
        return True

    def run_dialogue(self, tree_id):
        tree = self.dialogues.get(tree_id)
        if not tree:
            self.narrate("Nothing to say.")
            return
        self.state = GameState.DIALOGUE  # Temp lock
        node = tree.get('root')
        while node:
            self.narrate(node.get('text', ""))
            choices = node.get('choices', [])
            # Stub: auto-pick first (expand in next round)
            if not choices:
                break
            choice = choices[0]
            self.narrate(choice.get('text', ""))
            if 'action' in choice:
                self.handle_dialogue_action(choice['action'])
            if choice.get('end'):
                break
            node = tree.get(choice.get('next'))
        self.state = GameState.GAMEPLAY

    def handle_dialogue_action(self, action):
        if action.startswith("recruit_"):
            crew = action.replace("recruit_", "")
            self.set_flag(f"crew_{crew}")
            self.narrate(f"{crew} joins your crew!")

    def crew_count(self):
        return sum(1 for k in self.game_flags if k.startswith("crew_") and self.game_flags[k])

    def exhausted_text(self, obj):
        defaults = {
            "DEFAULT": "Nothing new here.",
            "seagull": "The seagull ignores you now."
        }
        return defaults.get(obj, "I've done that.")

    def show_hint(self):
        hints = self.hints.get(self.current_scene, ["No hints yet."])
        hint_index = self.game_flags.get(f"hint_{self.current_scene}", 0) % len(hints)
        self.narrate(hints[hint_index])
        self.set_flag(f"hint_{self.current_scene}", hint_index + 1)  # Escalate

    def narrate(self, text):
        self.narration_queue.append(text)
        if len(self.narration_queue) > 3:
            self.narration_queue.pop(0)

    def change_scene(self, scene_id):
        play_derez(self.screen)
        self.current_scene = scene_id
        self.room_title_time = pygame.time.get_ticks()

    def trigger_combine_effect(self):
        self.combine_pos = pygame.mouse.get_pos()
        self.combine_anim_time = pygame.time.get_ticks()

    def run(self):
        while self.running:
            game_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()
            self.screen.fill((0, 0, 0))
            # 1. Background & Details
            draw_scene_background(self.screen, self.current_scene, game_time)
            # 2. Hotspots with Pulsing Feedback (only if debug on)
            if self.debug_mode:
                scene = self.scenes.get(self.current_scene, {})
                for name, hs in scene.get('hotspots', {}).items():
                    rect_data = hs.get('rect')
                    if rect_data and not hs.get('exhausted'):
                        draw_hotspot_feedback(self.screen, rect_data, mouse_pos, game_time)
            # 3. Guybrush
            draw_guybrush(self.screen, (512, 510), game_time)
            # 4. Room Title Flash
            draw_room_title(self.screen, self.current_scene, self.room_title_time, game_time, self.font)
            # 5. UI & Inventory
            self.ui.draw_verb_grid(mouse_pos, self.selected_verb)
            draw_inventory_icons(self.screen, self.inventory)
            # Inventory Flash (yellow overlay)
            if game_time - self.inventory_flash_time < 1000:
                flash_idx = (len(self.inventory) - 1) % 6
                flash_rect = pygame.Rect(380 + flash_idx * 100, 590, 90, 40)
                pygame.draw.rect(self.screen, (255, 255, 0), flash_rect, 3)
            # 6. Effects & Cursor
            self.cursor_history.append(mouse_pos)
            if len(self.cursor_history) > 12: self.cursor_history.pop(0)
            draw_cursor_trail(self.screen, self.cursor_history)
            draw_combine_spiral(self.screen, self.combine_pos, self.combine_anim_time, game_time)
            self.ui.apply_glitch(self.glitch_intensity)
            self.glitch_intensity = max(0, self.glitch_intensity - 1)
            draw_vector_cursor(self.screen, mouse_pos, self.selected_verb, game_time)
            # 7. Narration
            for i, text in enumerate(self.narration_queue):
                surf = self.small_font.render(text[:40], True, (0, 255, 255))
                self.screen.blit(surf, (50, 700 - i * 25))
            # 8. Inventory Count
            inv_surf = self.font.render(f"Inv: {len(self.inventory)}", True, (0, 255, 255))
            self.screen.blit(inv_surf, (900, 580))
            for event in pygame.event.get():
                self.handle_event(event)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    manager = GameManager()
    manager.run()
