---

## 1. Background Asset Specifications

We are targeting a **1024x560** resolution for the play area (leaving the bottom 208px for the Verb Grid and Inventory).

| Room | Visual Description | Glitch/Paradox Element |
| --- | --- | --- |
| **Melee Docks** | Deep navy blues, painterly "Return" style pier. | The "High Street" sign is a blue hologram; water ripples are chunky 8-bit pixel blocks. |
| **SCUMM Bar** | Dim, warm orange glow. Dusty and sparse. | The missing piano keys emit a neon magenta "loading" bar effect. |
| **Lookout Point** | High altitude, purples and dark teals. | The moon occasionally "buffering" with a low-res spinning hourglass icon. |
| **Low-Tide Grove** | Overgrown greens and twisted trees. | The "Gap" is filled with "Mysts o' Tyme" (purple fog with floating hex-code particles). |
| **Governor's Mansion** | Cold, abandoned blue shadows and dust motes. | Portraits flicker between "Portrait of a Lady" and "404: Image Not Found." |

---

## 2. Character & Item Sprites

### Guybrush Idle Sprite Sheet

* **Dimensions:** 256x96 pixels (4 frames of 64x96).
* **Frame 1-2:** Classic breathing (slight shoulder movement).
* **Frame 3:** Blinking (Deadpan stare).
* **Frame 4: The Paradox:** Guybrush’s frock coat flashes into a silver NASA-style space suit for exactly 1/60th of a second.

### Rubber Chicken w/ Pulley Icon

* **Dimensions:** 64x64 pixels.
* **Visual:** Classic yellow latex chicken, but the pulley in the center is a glowing cyan **Singularity Core**.
* **Animation:** Use code to "vibrate" the sprite (random  pixel offset) to show it's out of phase.

---

## 3. Engine Implementation: `ui_manager.py` & Shaders

I've refined the `UIManager` to handle Claude's 12 verbs and added a "Paradox Shader" that we can trigger via game state.

### Verb Grid & Hover Logic

```python
import pygame

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Courier", 24, bold=True)
        self.verbs = [
            "GIVE", "OPEN", "CLOSE", "PICK UP", "LOOK AT", "USE",
            "TALK TO", "PUSH", "PULL", "HACK", "Q-ENTANGLE", "BUREAUCRATIZE"
        ]
        # Colors: Cyan and Magenta (The Official Colors of the Future-Past)
        self.CYAN = (0, 255, 255)
        self.MAGENTA = (255, 0, 255)

    def draw_verb_grid(self, mouse_pos, selected_verb):
        for i, verb in enumerate(self.verbs):
            x = 20 + (i % 3) * 110
            y = 580 + (i // 3) * 40
            rect = pygame.Rect(x, y, 100, 30)
            
            # Hover/Selection Logic
            is_hovered = rect.collidepoint(mouse_pos)
            color = self.MAGENTA if is_hovered or verb == selected_verb else self.CYAN
            
            text_surf = self.font.render(verb, True, color)
            self.screen.blit(text_surf, (x, y))
            
            # Subtle "Holo-Glow" for hovered verbs
            if is_hovered:
                glow = text_surf.copy()
                glow.set_alpha(100)
                self.screen.blit(glow, (x+2, y+2))

    def apply_paradox_glitch(self):
        """A simple scanline displacement 'shader' for when logic breaks."""
        screen_copy = self.screen.copy()
        for y in range(0, 768, 4):
            # Shift random rows by 5 pixels
            offset = 5 if (pygame.time.get_ticks() // 100) % 2 == 0 else -5
            self.screen.blit(screen_copy, (offset, y), (0, y, 1024, 4))

```

---

## 4. Asset Folder Structure

```text
/monkey-island-melee-prelude/
└── /assets/
    ├── /backgrounds/
    │   ├── docks_bg.png           # (1024x560)
    │   ├── scumm_bar_bg.png
    │   └── mansion_bg.png
    ├── /sprites/
    │   ├── guybrush_idle.png      # (256x96 sprite sheet)
    │   └── npc_bartender.png
    ├── /items/
    │   ├── chicken_pulley.png     # (64x64)
    │   └── grog_2_0.png
    └── /ui/
        ├── verb_cursor.png        # Holographic crosshair
        └── hint_book_icon.png

```

---

## 5. Graphics Lead: Transition Effect

Instead of a boring fade, use this **"De-Rez"** snippet in your scene transitions. It makes the screen collapse into a single horizontal line of pixels before expanding into the next room.

```python
def derez_transition(screen):
    for i in range(0, 384, 8):
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, 1024, i))
        pygame.draw.rect(screen, (0, 0, 0), (0, 768-i, 1024, i))
        pygame.display.flip()
        pygame.time.delay(10)

```

---

### Guybrush's Design Quip

"I've made sure the 'Q-Entangle' verb glows twice as bright as the others. If a player gets stuck, they'll probably just keep clicking it until the game crashes, which is technically a 'ending' if you're a speedrunner. Now, should I start drawing the **Sentient Vending Machine** for the SCUMM Bar, or focus on making the **3-Headed AI Monkey** look appropriately glitchy?"
