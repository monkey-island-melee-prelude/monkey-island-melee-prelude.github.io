import pygame
import math

def draw_scene_background(screen, room_id, game_time):
    """Draws vector backgrounds with new room-specific details."""
    screen.fill((5, 5, 25)) 
    
    if room_id == 'melee_docks':
        pygame.draw.rect(screen, (40, 30, 20), (0, 450, 1024, 110)) 
        pygame.draw.rect(screen, (0, 30, 80), (0, 560, 1024, 208))
        # New Detail: The "Seagull" (a flickering white dot)
        bird_bob = int(math.sin(game_time * 0.002) * 5)
        pygame.draw.circle(screen, (255, 255, 255), (800, 300 + bird_bob), 3)
        pygame.draw.line(screen, (200, 200, 200), (795, 300 + bird_bob), (805, 295 + bird_bob), 1)

    elif room_id == 'scumm_bar':
        pygame.draw.rect(screen, (50, 30, 10), (0, 400, 1024, 160))
        # New Detail: Piano Keys
        for i in range(10):
            pygame.draw.rect(screen, (255, 255, 255), (700 + i*12, 430, 10, 25))
        for x in [200, 500]: # Tables
            pygame.draw.rect(screen, (80, 50, 20), (x-60, 420, 120, 20))

    elif room_id == 'lookout_point':
        pygame.draw.polygon(screen, (20, 20, 20), [(0, 560), (400, 350), (1024, 560)])
        pygame.draw.circle(screen, (220, 220, 180), (850, 120), 45)
        # New Detail: Distant Melee Lights
        for i in range(5):
            pygame.draw.circle(screen, (255, 255, 0), (100 + i*30, 500 + i*5), 2)

    elif room_id == 'low_tide_grove':
        pygame.draw.rect(screen, (10, 30, 10), (0, 500, 1024, 60))
        for x in [150, 450, 850]:
            pygame.draw.polygon(screen, (5, 50, 5), [(x, 500), (x+40, 250), (x+80, 500)])
        # New Detail: Fireflies
        for i in range(3):
            fx = (x + math.sin(game_time * 0.001 + i) * 50) % 1024
            fy = 300 + math.cos(game_time * 0.002 + i) * 20
            pygame.draw.circle(screen, (150, 255, 150), (int(fx), int(fy)), 2)

def draw_vector_cursor(screen, pos, verb, game_time):
    """Draws a custom icon at the mouse position based on the verb."""
    x, y = pos
    color = (255, 255, 255)
    
    if verb in ["PICK UP", "USE", "GIVE"]:
        # Hand Icon
        pygame.draw.circle(screen, color, (x, y), 8, 1)
        pygame.draw.line(screen, color, (x, y-8), (x, y-15), 2) # Fingers stub
    elif verb == "TALK TO":
        # Speech Bubble
        pygame.draw.ellipse(screen, color, (x-10, y-10, 20, 15), 1)
        pygame.draw.polygon(screen, color, [(x, y+5), (x-5, y+10), (x+5, y+5)])
    elif verb == "HACK":
        # Wrench
        pygame.draw.rect(screen, color, (x-2, y-10, 4, 20))
        pygame.draw.circle(screen, color, (x, y-10), 6, 2)
    elif verb == "Q-ENTANGLE":
        # Quantum Swirl
        for i in range(3):
            angle = (game_time * 0.01 + i) % (math.pi * 2)
            px = x + math.cos(angle) * 10
            py = y + math.sin(angle) * 10
            pygame.draw.circle(screen, (0, 255, 255), (int(px), int(py)), 2)
    else:
        # Default Crosshair
        pygame.draw.line(screen, color, (x-10, y), (x+10, y), 1)
        pygame.draw.line(screen, color, (x, y-10), (x, y+10), 1)

def draw_hotspot_feedback(screen, rect_data, mouse_pos, game_time):
    """Draws a pulsing hover effect for hotspots."""
    r = pygame.Rect(rect_data[0], rect_data[1], 
                    rect_data[2]-rect_data[0], 
                    rect_data[3]-rect_data[1])
    
    if r.collidepoint(mouse_pos):
        # Pulse alpha/thickness
        pulse = int((math.sin(game_time * 0.01) + 1) * 2) + 1
        pygame.draw.rect(screen, (255, 0, 255), r, pulse)
    else:
        pygame.draw.rect(screen, (0, 255, 255), r, 1)
