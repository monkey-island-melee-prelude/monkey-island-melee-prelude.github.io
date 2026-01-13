import pygame
import math

def draw_scene_background(screen, room_id, game_time):
    """Draws vector backgrounds with room-specific details."""
    screen.fill((5, 5, 25)) 
    
    if room_id == 'melee_docks':
        pygame.draw.rect(screen, (40, 30, 20), (0, 450, 1024, 110)) 
        pygame.draw.rect(screen, (0, 30, 80), (0, 560, 1024, 208))
        bird_bob = int(math.sin(game_time * 0.002) * 5)
        pygame.draw.circle(screen, (255, 255, 255), (800, 300 + bird_bob), 3)
        pygame.draw.line(screen, (200, 200, 200), (795, 300 + bird_bob), (805, 295 + bird_bob), 1)

    elif room_id == 'scumm_bar':
        pygame.draw.rect(screen, (50, 30, 10), (0, 400, 1024, 160))
        for i in range(10):
            pygame.draw.rect(screen, (255, 255, 255), (700 + i*12, 430, 10, 25))
        for x in [200, 500]: # Tables
            pygame.draw.rect(screen, (80, 50, 20), (x-60, 420, 120, 20))

    elif room_id == 'lookout_point':
        pygame.draw.polygon(screen, (20, 20, 20), [(0, 560), (400, 350), (1024, 560)])
        pygame.draw.circle(screen, (220, 220, 180), (850, 120), 45)
        for i in range(5):
            pygame.draw.circle(screen, (255, 255, 0), (100 + i*30, 500 + i*5), 2)

    elif room_id == 'low_tide_grove':
        pygame.draw.rect(screen, (10, 30, 10), (0, 500, 1024, 60))
        for x in [150, 450, 850]:
            pygame.draw.polygon(screen, (5, 50, 5), [(x, 500), (x+40, 250), (x+80, 500)])
        for i in range(3):
            fx = (x + math.sin(game_time * 0.001 + i) * 50) % 1024
            fy = 300 + math.cos(game_time * 0.002 + i) * 20
            pygame.draw.circle(screen, (150, 255, 150), (int(fx), int(fy)), 2)

    elif room_id == 'governors_mansion':
        pygame.draw.ellipse(screen, (120, 10, 10), (200, 480, 624, 70))
        pygame.draw.rect(screen, (180, 150, 50), (450, 150, 124, 180), 6)

def draw_guybrush(screen, pos, game_time):
    x, y = pos
    bob = int(math.sin(game_time * 0.005) * 2)
    is_glitching = (game_time % 5000) < 150
    color = (0, 255, 255) if is_glitching else (240, 240, 240)
    pygame.draw.line(screen, color, (x, y-60+bob), (x, y-20+bob), 3) # Torso
    pygame.draw.circle(screen, (255, 210, 180), (x, y-75+bob), 12) # Head
    pygame.draw.line(screen, color, (x, y-20+bob), (x-15, y), 3) # L-Leg
    pygame.draw.line(screen, color, (x, y-20+bob), (x+15, y), 3) # R-Leg
    if is_glitching:
        pygame.draw.circle(screen, (0, 255, 255), (x, y-75+bob), 18, 1)

def draw_inventory_icons(screen, items):
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
            pygame.draw.line(screen, (255, 255, 255), (x + 15, y + 15), (x + 30, y + 15), 2)

def draw_cursor_trail(screen, history):
    for i, pos in enumerate(history):
        alpha = int((i / len(history)) * 255)
        size = int((i / len(history)) * 4)
        color = (0, 100, 100) if i < 5 else (0, 200, 200)
        pygame.draw.circle(screen, color, pos, size)

def draw_combine_spiral(screen, pos, start_time, current_time):
    elapsed = current_time - start_time
    if elapsed > 500: return
    for i in range(5):
        angle = (elapsed * 0.02) + (i * 1.2)
        dist = (elapsed * 0.1)
        px = pos[0] + math.cos(angle) * dist
        py = pos[1] + math.sin(angle) * dist
        color = (0, 255, 255) if i % 2 == 0 else (255, 0, 255)
        pygame.draw.circle(screen, color, (int(px), int(py)), 3)

def draw_room_title(screen, name, start_time, current_time, font):
    elapsed = current_time - start_time
    if elapsed > 2000: return
    alpha = max(0, 255 - int((elapsed / 2000) * 255))
    text_surf = font.render(name.replace('_', ' ').upper(), True, (0, 255, 255))
    text_surf.set_alpha(alpha)
    rect = text_surf.get_rect(center=(512, 200))
    screen.blit(text_surf, rect)

def draw_hotspot_feedback(screen, rect_data, mouse_pos, game_time):
    r = pygame.Rect(rect_data[0], rect_data[1], 
                    rect_data[2]-rect_data[0], 
                    rect_data[3]-rect_data[1])
    
    if r.collidepoint(mouse_pos):
        pulse = int((math.sin(game_time * 0.01) + 1) * 2) + 1
        pygame.draw.rect(screen, (255, 0, 255), r, pulse)
    else:
        pygame.draw.rect(screen, (0, 255, 255), r, 1)

def play_derez(screen):
    for i in range(0, 512, 16):
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, 1024, i))
        pygame.draw.rect(screen, (0, 0, 0), (0, 1024 - i, 1024, i))
        pygame.display.flip()
        pygame.time.delay(10)
