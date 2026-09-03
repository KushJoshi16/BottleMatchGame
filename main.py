import pygame
import sys
import random
import colorsys
import tkinter as tk
from tkinter import simpledialog

# Initialize Pygame
# pygame.init()
# WIDTH, HEIGHT = 900, 650
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Bottle Matching Puzzle - Animated")
# clock = pygame.time.Clock()
# font = pygame.font.SysFont("Arial", 24)
# title_font = pygame.font.SysFont("Arial", 32, bold=True)

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bottle Matching Puzzle")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 24)
title_font = pygame.font.SysFont("Arial", 32, bold=True)

# Color Templates
BACKGROUND = (240, 245, 250)
GLASS_COLOR = (50, 50, 50)
CAP_COLOR = (100, 100, 100)
HIDDEN_BOX_COLOR = (180, 190, 200)
TEXT_COLOR = (44, 62, 80)
BTN_COLOR = (46, 204, 113)
BTN_HOVER_COLOR = (39, 174, 96)

def choose_n_pygame():
    """Renders a simple menu allowing the user to select N via keyboard input."""
    input_n = 5  # Default initialization selection
    menu_running = True
    
    while menu_running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    menu_running = False
                elif event.key == pygame.K_UP:
                    input_n = min(10, input_n + 1)
                elif event.key == pygame.K_DOWN:
                    input_n = max(3, input_n - 1)
                    
        screen.fill(BACKGROUND)
        
        # Display instructions
        t1 = title_font.render("Bottle Match Game Setup", True, TEXT_COLOR)
        t2 = font.render(f"Use UP / DOWN Arrow Keys to set total bottles", True, TEXT_COLOR)
        t3 = title_font.render(f"Number of Bottles (N): {input_n}", True, (52, 152, 219))
        t4 = font.render("Press ENTER / RETURN to Start Match Puzzle", True, BTN_HOVER_COLOR)
        
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, 180))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, 250))
        screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, 320))
        screen.blit(t4, (WIDTH // 2 - t4.get_width() // 2, 420))
        
        pygame.display.flip()
        clock.tick(60)
        
    return input_n

# Run menu safely right before launching coordinates
N = choose_n_pygame()

# --- STEP 2: GENERATE DISTINCT COLORS BASED ON N ---
def generate_distinct_colors(n):
    """Generates N highly contrasting colors evenly spaced around the color wheel."""
    colors = []
    for i in range(n):
        hue = i / n 
        saturation = 0.85  
        brightness = 0.90  
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
        colors.append((int(r * 255), int(g * 255), int(b * 255)))
    return colors

DISTINCT_COLORS = generate_distinct_colors(N)

# BACKGROUND = (240, 245, 250)
# GLASS_COLOR = (50, 50, 50)
# CAP_COLOR = (100, 100, 100)
# HIDDEN_BOX_COLOR = (180, 190, 200)
# TEXT_COLOR = (44, 62, 80)
# BTN_COLOR = (46, 204, 113)
# BTN_HOVER_COLOR = (39, 174, 96)

class Bottle:
    """Manages individual bottle rendering positions for smooth sliding."""
    def __init__(self, color_idx, start_x, start_y):
        self.color_idx = color_idx
        self.x = float(start_x)
        self.y = float(start_y)
        self.target_x = float(start_x)
        self.target_y = float(start_y)

    def update(self, speed=0.15):
        """Linearly interpolates current position toward target position."""
        if abs(self.x - self.target_x) > 0.1:
            self.x += (self.target_x - self.x) * speed
        else:
            self.x = self.target_x

        if abs(self.y - self.target_y) > 0.1:
            self.y += (self.target_y - self.y) * speed
        else:
            self.y = self.target_y

    def is_animating(self):
        return self.x != self.target_x or self.y != self.target_y


class GameState:
    def __init__(self, n):
        self.n = n
        self.colors = DISTINCT_COLORS[:n]
        
        # Target arrangement
        self.target_sequence = list(range(n))
        random.shuffle(self.target_sequence)
        
        # Player arrangement layout math
        self.bottle_w = 80
        self.bottle_h = 160
        total_w = n * self.bottle_w + (n - 1) * 40
        self.start_x = (WIDTH - total_w) // 2
        
        self.hidden_y = 120
        self.player_y = 360
        
        # Shuffle player layout safely
        player_indices = list(range(n))
        while player_indices == self.target_sequence:
            random.shuffle(player_indices)

        # Create Bottle objects at their initial slots
        self.bottles = []
        for i in range(n):
            initial_slot = player_indices[i]
            x_pos = self.get_slot_x(i)
            self.bottles.append(Bottle(initial_slot, x_pos, self.player_y))
            
        self.selected_index = None
        self.game_won = False
        self.btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 80, 200, 50)

    def get_slot_x(self, index):
        return self.start_x + index * (self.bottle_w + 40)

    def check_matches(self):
        # Don't check for victory while bottles are still actively sliding
        if any(b.is_animating() for b in self.bottles):
            return sum(1 for i, b in enumerate(self.bottles) if b.color_idx == self.target_sequence[i])

        matches = sum(1 for i, b in enumerate(self.bottles) if b.color_idx == self.target_sequence[i])
        if matches == self.n:
            self.game_won = True
        return matches

    def get_clicked_bottle(self, pos):
        if self.game_won or any(b.is_animating() for b in self.bottles):
            return None  # Block inputs during animations or after victory
            
        x, y = pos
        for i in range(self.n):
            bx = self.get_slot_x(i)
            rect = pygame.Rect(bx, self.player_y, self.bottle_w, self.bottle_h)
            if rect.collidepoint(x, y):
                return i
        return None

    def swap_bottles(self, idx1, idx2):
        # Swap target positions
        pos1 = self.bottles[idx1].target_x
        pos2 = self.bottles[idx2].target_x
        
        self.bottles[idx1].target_x = pos2
        self.bottles[idx2].target_x = pos1
        
        # Swap positions inside our Python tracking array to maintain index order
        self.bottles[idx1], self.bottles[idx2] = self.bottles[idx2], self.bottles[idx1]


def draw_bottle(surface, x, y, width, height, liquid_color, is_hidden=False):
    if is_hidden:
        # Draw a mystery gray slot/box instead of a bottle
        box_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, HIDDEN_BOX_COLOR, box_rect, border_radius=15)
        question_mark = title_font.render("?", True, BACKGROUND)
        surface.blit(question_mark, (x + width//2 - 10, y + height//2 - 20))
        return

    body_height = int(height * 0.65)
    neck_height = int(height * 0.25)
    cap_height = int(height * 0.10)
    neck_width = int(width * 0.35)
    
    # 1. Liquid Fill
    max_liquid_h = int(body_height * 0.90)
    liquid_rect = pygame.Rect(x + 6, y + cap_height + neck_height + body_height - max_liquid_h - 6, width - 12, max_liquid_h)
    pygame.draw.rect(surface, liquid_color, liquid_rect, border_bottom_left_radius=10, border_bottom_right_radius=10)

    # 2. Glass Body
    body_rect = pygame.Rect(x, y + cap_height + neck_height, width, body_height)
    pygame.draw.rect(surface, GLASS_COLOR, body_rect, width=5, border_bottom_left_radius=15, border_bottom_right_radius=15)

    # 3. Glass Neck (Fixed tuple concatenation here)
    neck_top_left = (x + (width - neck_width) // 2, y + cap_height)
    neck_top_right = (neck_top_left[0] + neck_width, y + cap_height)
    body_top_right = (x + width - 2, y + cap_height + neck_height)
    body_top_left = (x + 2, y + cap_height + neck_height)
    pygame.draw.polygon(surface, GLASS_COLOR, [neck_top_left, neck_top_right, body_top_right, body_top_left], width=5)

    # 4. Cap
    cap_rect = pygame.Rect(neck_top_left[0] - 2, y, neck_width + 4, cap_height)
    pygame.draw.rect(surface, CAP_COLOR, cap_rect, border_top_left_radius=4, border_top_right_radius=4)



# Initialize game state
game = GameState(N)

# Main Loop
while True:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game.game_won and game.btn_rect.collidepoint(mouse_pos):
                    game = GameState(N)
                    continue
                
                clicked_idx = game.get_clicked_bottle(mouse_pos)
                if clicked_idx is not None:
                    if game.selected_index is None:
                        game.selected_index = clicked_idx
                    else:
                        if game.selected_index != clicked_idx:
                            game.swap_bottles(game.selected_index, clicked_idx)
                        game.selected_index = None

    # Update Positions for animations
    for bottle in game.bottles:
        bottle.update()

    # Clear screen
    screen.fill(BACKGROUND)

    # UI Text
    matches = game.check_matches()
    
    title_text = title_font.render("Bottle Matching Puzzle", True, TEXT_COLOR)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))
    
    target_label = font.render("Target Arrangement (Hidden)", True, TEXT_COLOR)
    screen.blit(target_label, (game.start_x, game.hidden_y - 35))
    
    player_label = font.render("Your Arrangement (Swap Active)", True, TEXT_COLOR)
    screen.blit(player_label, (game.start_x, game.player_y - 35))

    status_str = f"Matching Bottles: {matches} / {game.n}" if not game.game_won else "Success! All bottles match!"
    status_text = title_font.render(status_str, True, BTN_HOVER_COLOR if game.game_won else TEXT_COLOR)
    screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, 300))

    # 1. Render Target (Hidden) Row
    for i in range(game.n):
        bx = game.get_slot_x(i)
        color_idx = game.target_sequence[i]
        bottle_color = game.colors[color_idx]
        draw_bottle(screen, bx, game.hidden_y, game.bottle_w, game.bottle_h, bottle_color, is_hidden=not game.game_won)

    # 2. Render Selection Box Border (Kept fixed at the slot position)
    if game.selected_index is not None:
        sel_x = game.get_slot_x(game.selected_index)
        pygame.draw.rect(screen, (52, 152, 219), (sel_x - 6, game.player_y - 6, game.bottle_w + 12, game.bottle_h + 12), width=4, border_radius=10)

    # 3. Render Player Row using each bottle's live animated coordinates
    for bottle in game.bottles:
        bottle_color = game.colors[bottle.color_idx]
        draw_bottle(screen, bottle.x, bottle.y, game.bottle_w, game.bottle_h, bottle_color, is_hidden=False)

    # 4. Win Button
    if game.game_won:
        current_btn_color = BTN_HOVER_COLOR if game.btn_rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, current_btn_color, game.btn_rect, border_radius=8)
        btn_text = font.render("New Game", True, (255, 255, 255))
        screen.blit(btn_text, (game.btn_rect.x + (game.btn_rect.width - btn_text.get_width()) // 2, game.btn_rect.y + 12))

    pygame.display.flip()
    clock.tick(60)
