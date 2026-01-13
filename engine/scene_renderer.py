import pygame
import math

def draw_scene_background(screen, room_id):
    """Draws simple vector-based backgrounds for the 5 rooms."""
    screen.fill((5, 5, 25)) # Deep midnight blue base
    
    if room_id == 'melee_docks':
        # The Pier
        pygame.draw.rect(screen, (40, 30, 20), (0, 450, 1024, 110)) 
        # The Water
        pygame.draw.rect(screen, (0, 30, 80), (0, 560, 1024, 208))
        for i in range(3): # Sparkles
            y = 580 + i * 40
            pygame.draw.line(screen, (0, 100, 200), (0, y), (1024, y), 1)

    elif room_id == 'scumm_bar':
        # Floor
        pygame.draw.rect(screen, (50, 30, 10), (0, 400, 1024, 160))
        # Tables (Simplified)
        for x in [200, 500, 800]:
            pygame.draw.rect(screen, (80, 50, 20), (x-60, 420, 120, 20)) # Top
            pygame.draw.rect(screen, (60, 40, 15), (x-10, 440, 20, 40))  # Leg

    elif room_id == 'lookout_point':
        # Cliff edge
        pygame.draw.polygon(screen, (20, 20, 20), [(0, 560), (400, 350), (1024, 560)])
        # The Moon
        pygame.draw.circle(screen, (220, 220, 180), (850, 120), 45)

    elif room_id == 'low_tide_grove':
        # Ground
        pygame.draw.rect(screen, (10, 30, 10), (0, 500, 1024, 60))
        # Trees (Triangles)
        for x in [150, 450, 850]:
            pygame.draw.polygon(screen, (5, 50, 5), [(x, 500), (x+40, 250), (x+80, 500)])

    elif room_id == 'governors_mansion':
        # Rug
        pygame.draw.ellipse(screen, (120, 10, 10), (200, 480, 624, 70))
        # Portrait Frame
        pygame.draw.rect(screen, (180, 150, 50), (450, 150, 124, 180), 6)

def draw_guybrush(screen, pos, game_time):
    """Renders the stick-figure Guybrush with a breathing animation and glitch."""
    x, y = pos
    # Breathing bob: moves between 0 and 2 pixels based on time
    bob = int(math.sin(game_time * 0.005) * 2)
    
    # Glitch logic: Space Suit appears for 150ms every 5 seconds
    is_glitching = (game_time % 5000) < 150
    color = (0, 255, 255) if is_glitching else (240, 240, 240)
    
    # Body (Head, torso, legs)
    pygame.draw.line(screen, color, (x, y-60+bob), (x, y-20+bob), 3) # Torso
    pygame.draw.circle(screen, (255, 210, 180), (x, y-75+bob), 12)   # Head
    pygame.draw.line(screen, color, (x, y-20+bob), (x-15, y), 3)     # L-Leg
    pygame.draw.line(screen, color, (x, y-20+bob), (x+15, y), 3)     # R-Leg
    
    if is_glitching: # Space Suit Helmet
        pygame.draw.circle(screen, (0, 255, 255), (x, y-75+bob), 18, 1)

def draw_inventory_icons(screen, items):
    """Draws geometric icons for the inventory slots."""
    for i, item in enumerate(items[:6]):
        x = 380 + i * 100
        y = 610
        if item == "rope":
            pygame.draw.circle(screen, (139, 69, 19), (x+20, y+10), 12, 2)
        elif item == "rubber_chicken":
            pygame.draw.ellipse(screen, (255, 255, 0), (x+10, y, 20, 30))
            pygame.draw.circle(screen, (0, 255, 255), (x+20, y+15), 6, 1) # Pulley
        elif item == "grog_2.0":
            pygame.draw.rect(screen, (50, 200, 50), (x+12, y, 16, 28))
