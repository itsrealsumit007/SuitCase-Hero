import pygame
import random
import math

pygame.init()

WIDTH = 800
HEIGHT = 600
FPS = 60
SUITCASE_SPEED = 5
SUITCASE_DIM = (50, 50)
LUNCH_BONUS_POINTS = 50
SCHOOL_ITEMS = ['NOTEBOOK', 'PENCIL', 'LUNCHBOX']

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SuitCase Hero")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

DIRECTIONS = ['LEFT', 'RIGHT', 'UP', 'DOWN']
LUGGAGE_TYPES = {
    'CARRY_ON': {'rarity': 'COMMON', 'points': 10, 'speed': SUITCASE_SPEED},
    'BACKPACK': {'rarity': 'COMMON', 'points': 15, 'speed': SUITCASE_SPEED * 1.2},
    'CHECKED_BAG': {'rarity': 'RARE', 'points': 25, 'speed': SUITCASE_SPEED * 1.5},
    'VINTAGE_TRUNK': {'rarity': 'EPIC', 'points': 50, 'speed': SUITCASE_SPEED * 2},
    'FIRST_CLASS': {'rarity': 'LEGENDARY', 'points': 100, 'speed': SUITCASE_SPEED * 2.5}
}

COLORS = {
    'COMMON': (139, 69, 19),
    'RARE': (255, 215, 0),
    'EPIC': (148, 0, 211),
    'LEGENDARY': (255, 140, 0),
    'WRONG_KEY': (255, 0, 0),
    'CONVEYOR': (128, 128, 128),
    'UI_BLUE': (65, 105, 225),
    'UI_GOLD': (255, 223, 0),
    'BACKGROUND': (240, 248, 255)
}

CATCH_ZONE_HEIGHT = 100
CATCH_ZONE_Y = HEIGHT - CATCH_ZONE_HEIGHT - 50
CATCH_ZONE_COLOR = (200, 200, 200, 128)

TITLE_FONT_SIZE = 48
REGULAR_FONT_SIZE = 24
SMALL_FONT_SIZE = 18

BASE_SPAWN_INTERVAL = 150
MIN_SPAWN_INTERVAL = 30
DIFFICULTY_INCREASE_THRESHOLD = 500
SPEED_INCREASE_RATE = 1.2

GAME_STATES = {
    'START': 0,
    'PLAYING': 1,
    'GAME_OVER': 2
}

UI_COLORS = {
    'PANEL_BG': (65, 105, 225),
    'PANEL_BORDER': (255, 215, 0),
    'TEXT_PRIMARY': (255, 255, 255),
    'TEXT_SECONDARY': (255, 255, 150),
    'ACCENT': (255, 140, 0),
    'SUCCESS': (50, 205, 50),
    'WARNING': (255, 99, 71),
    'PROGRESS_BG': (135, 206, 250),
}

CATCH_ZONE_ACTIVE_COLOR = (87, 217, 163, 100)
CATCH_ZONE_INACTIVE_COLOR = (65, 105, 225, 50)

class FallingBag(pygame.sprite.Sprite):
    def __init__(self, x, y, bag_type, speed_multiplier=1.0):
        super().__init__()
        self.type = bag_type
        self.direction = random.choice(DIRECTIONS)
        self.speed = bag_type['speed'] * speed_multiplier
        
        self.image = pygame.Surface(SUITCASE_DIM)
        self.image.fill(COLORS[bag_type['rarity']])
        
        arrow_color = WHITE
        arrow_size = 20
        arrow_margin = 5
        
        if self.direction == 'LEFT':
            pygame.draw.polygon(self.image, arrow_color, 
                [(arrow_size, arrow_margin), 
                 (0, SUITCASE_DIM[1]//2),
                 (arrow_size, SUITCASE_DIM[1]-arrow_margin)])
        elif self.direction == 'RIGHT':
            pygame.draw.polygon(self.image, arrow_color,
                [(SUITCASE_DIM[0]-arrow_size, arrow_margin),
                 (SUITCASE_DIM[0], SUITCASE_DIM[1]//2),
                 (SUITCASE_DIM[0]-arrow_size, SUITCASE_DIM[1]-arrow_margin)])
        elif self.direction == 'UP':
            pygame.draw.polygon(self.image, arrow_color,
                [(SUITCASE_DIM[0]//2, arrow_margin),
                 (arrow_margin, arrow_size),
                 (SUITCASE_DIM[0]-arrow_margin, arrow_size)])
        else:
            pygame.draw.polygon(self.image, arrow_color,
                [(SUITCASE_DIM[0]//2, SUITCASE_DIM[1]-arrow_margin),
                 (arrow_margin, SUITCASE_DIM[1]-arrow_size),
                 (SUITCASE_DIM[0]-arrow_margin, SUITCASE_DIM[1]-arrow_size)])
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.caught = False
        self.wrong_key_pressed = False
        
        self.has_lunch = random.random() < 0.1
        if self.has_lunch:
            pygame.draw.rect(self.image, WHITE, (10, 15, 30, 20))

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.kill()
            global combo
            if not self.caught:
                combo = 0

    def collect(self):
        points = self.type['points']
        if self.has_lunch:
            points += LUNCH_BONUS_POINTS
        return points

all_sprites = pygame.sprite.Group()
falling_bags = pygame.sprite.Group()

score = 0
combo = 0
max_combo = 0
difficulty_level = 1

title_font = pygame.font.SysFont("Arial Black", TITLE_FONT_SIZE)
regular_font = pygame.font.SysFont("Arial", REGULAR_FONT_SIZE)
small_font = pygame.font.SysFont("Arial", SMALL_FONT_SIZE)

def draw_ui_panel(surface, x, y, width, height, color=UI_COLORS['PANEL_BG']):
    panel = pygame.Surface((width, height))
    panel.fill(color)
    panel.set_alpha(230)
    surface.blit(panel, (x, y))
    
    pygame.draw.rect(surface, UI_COLORS['PANEL_BORDER'], 
                    (x, y, width, height), 2)
    
    highlight = pygame.Surface((width, 2))
    highlight.fill(UI_COLORS['PANEL_BORDER'])
    highlight.set_alpha(150)
    surface.blit(highlight, (x, y))

def draw_progress_bar(surface, x, y, width, height, progress, max_value):
    pygame.draw.rect(surface, UI_COLORS['PROGRESS_BG'], (x, y, width, height))
    
    progress_width = int((progress / max_value) * width)
    if progress_width > 0:
        pygame.draw.rect(surface, UI_COLORS['ACCENT'], 
                        (x, y, progress_width, height))
    
    pygame.draw.rect(surface, UI_COLORS['PANEL_BORDER'], 
                    (x, y, width, height), 1)

def draw_game_stats(surface, stats_x, stats_y, game_vars):
    panel_width = 250
    panel_height = 250
    draw_ui_panel(surface, stats_x, stats_y, panel_width, panel_height)
    
    score_y = stats_y + 30
    score_label = small_font.render("SCORE 🎯", True, UI_COLORS['TEXT_SECONDARY'])
    score_value = regular_font.render(f"{score:,}", True, UI_COLORS['ACCENT'])
    surface.blit(score_label, (stats_x + 20, score_y))
    surface.blit(score_value, (stats_x + 20, score_y + 25))

    combo_y = score_y + 80
    combo_label = small_font.render("COMBO ⭐", True, UI_COLORS['TEXT_SECONDARY'])
    combo_color = UI_COLORS['SUCCESS'] if combo > 10 else UI_COLORS['TEXT_PRIMARY']
    combo_value = regular_font.render(f"{combo}x", True, combo_color)
    surface.blit(combo_label, (stats_x + 20, combo_y))
    surface.blit(combo_value, (stats_x + 20, combo_y + 25))

    lives_y = combo_y + 80
    lives_label = small_font.render("LIVES ❤️", True, UI_COLORS['TEXT_SECONDARY'])
    surface.blit(lives_label, (stats_x + 20, lives_y))
    
    heart_spacing = 30
    for i in range(game_vars['lives']):
        bounce_offset = abs(math.sin(pygame.time.get_ticks() * 0.005 + i) * 3)
        heart = regular_font.render("♥", True, UI_COLORS['WARNING'])
        surface.blit(heart, (stats_x + 20 + (i * heart_spacing), lives_y + 25 - bounce_offset))
def draw_game_header(surface):
    header_height = 60
    draw_ui_panel(surface, 0, 0, WIDTH, header_height)
    
    title_bounce = abs(math.sin(pygame.time.get_ticks() * 0.003) * 3)
    title = title_font.render("✈️ SUITCASE HERO ✈️", True, UI_COLORS['ACCENT'])
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 10 + title_bounce))
    
    level_text = small_font.render(f"LEVEL {difficulty_level} ⭐", True, UI_COLORS['TEXT_SECONDARY'])
    surface.blit(level_text, (WIDTH - 150, 20))

def draw_game_screen(stats, belt_offset, messages):
    screen.fill(COLORS['BACKGROUND'])
    
    for y in range(0, CATCH_ZONE_HEIGHT, 20):
        belt_y = CATCH_ZONE_Y + y + belt_offset
        pygame.draw.line(screen, UI_COLORS['PANEL_BORDER'], 
            (0, belt_y), (WIDTH, belt_y), 3)
    
    belt_overlay = pygame.Surface((WIDTH, CATCH_ZONE_HEIGHT))
    belt_overlay.fill(UI_COLORS['PANEL_BG']) 
    belt_overlay.set_alpha(100)
    screen.blit(belt_overlay, (0, CATCH_ZONE_Y))
    
    pygame.draw.line(screen, UI_COLORS['PANEL_BORDER'], 
        (0, CATCH_ZONE_Y), (WIDTH, CATCH_ZONE_Y), 2)
    pygame.draw.line(screen, UI_COLORS['PANEL_BORDER'], 
        (0, HEIGHT - 1), (WIDTH, HEIGHT - 1), 2)
    
    draw_game_header(screen)
    draw_game_stats(screen, 20, 80, stats)
    
    all_sprites.draw(screen)
    
    if combo in messages:
        msg = messages[combo]
        text = regular_font.render(msg, True, UI_COLORS['ACCENT'])
        
        text_x = WIDTH//2 - text.get_width()//2
        text_y = HEIGHT//2 - 50
        bounce = abs(math.sin(pygame.time.get_ticks() * 0.005) * 10)
        
        bg = pygame.Surface((text.get_width() + 40, text.get_height() + 20))
        bg.fill(UI_COLORS['PANEL_BG'])
        bg.set_alpha(200)
        
        screen.blit(bg, (text_x - 20, text_y + bounce - 10))
        screen.blit(text, (text_x, text_y + bounce))

def draw_start_screen():
    screen.fill(COLORS['BACKGROUND'])
    
    panel_width = 600
    panel_height = 400
    panel_x = WIDTH//2 - panel_width//2
    panel_y = HEIGHT//2 - panel_height//2
    draw_ui_panel(screen, panel_x, panel_y, panel_width, panel_height)
    
    title = title_font.render("SUITCASE HERO", True, UI_COLORS['ACCENT'])
    screen.blit(title, (WIDTH//2 - title.get_width()//2, panel_y + 40))
    
    instructions = [
        "Match the arrow keys with the suitcase directions",
        "Catch them on the conveyor belt",
        "Get bonus points for lunch boxes!",
        "Don't let too many suitcases fall",
        "",
        "Press SPACE to start!"
    ]
    
    for i, text in enumerate(instructions):
        color = UI_COLORS['ACCENT'] if i == len(instructions)-1 else UI_COLORS['TEXT_PRIMARY']
        instruction = regular_font.render(text, True, color)
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, 
                                panel_y + 150 + i * 40))

def draw_game_over_screen():
    draw_ui_panel(screen, WIDTH//2 - 250, HEIGHT//2 - 150, 500, 300, COLORS['WRONG_KEY'])
    
    game_over = title_font.render("GAME OVER!", True, WHITE)
    screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, HEIGHT//2 - 100))
    
    score_text = regular_font.render(f"Final Score: {score}", True, COLORS['UI_GOLD'])
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    
    combo_text = regular_font.render(f"Max Combo: {max_combo}", True, COLORS['UI_GOLD'])
    screen.blit(combo_text, (WIDTH//2 - combo_text.get_width()//2, HEIGHT//2 + 40))
    
    diff_text = regular_font.render(f"Difficulty Reached: {difficulty_level}", True, COLORS['UI_GOLD'])
    screen.blit(diff_text, (WIDTH//2 - diff_text.get_width()//2, HEIGHT//2 + 80))
    
    restart = regular_font.render("Press SPACE to play again! 🎮", True, UI_COLORS['SUCCESS'])
    quit_text = regular_font.render("Press ESC to quit ❌", True, UI_COLORS['WARNING'])
    screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 140))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 180))

def run_game():
    global score, combo, max_combo, difficulty_level

    game_clock = pygame.time.Clock()
    running = True
    current_state = GAME_STATES['START']
    best_combo = 0
    belt_offset = 0
    items_in_zone = False

    combo_texts = {
        5: "HIGH FIVE! 🎒",
        10: "SUPER STAR! ⭐", 
        15: "AMAZING! 🌟",
        20: "INCREDIBLE! 🏆",
        25: "LEGENDARY! 👑"
    }

    def reset_game():
        global score, combo, difficulty_level
        score = 0
        combo = 0
        difficulty_level = 1
        all_sprites.empty()
        falling_bags.empty()
        return {
            'spawn_timer': 0,
            'spawn_times': [BASE_SPAWN_INTERVAL],
            'speed_multiplier': 1.0,
            'difficulty_level': 1,
            'last_difficulty_increase': 0,
            'missed_bags': 0,
            'lives': 3
        }

    game_vars = reset_game()

    while running:
        events = pygame.event.get()
        
        screen.fill(COLORS['BACKGROUND'])

        items_in_zone = False
        for bag in falling_bags:
            if bag.rect.colliderect(pygame.Rect(0, CATCH_ZONE_Y, WIDTH, CATCH_ZONE_HEIGHT)):
                items_in_zone = True
                break
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if current_state == GAME_STATES['START']:
                        current_state = GAME_STATES['PLAYING']
                        game_vars = reset_game()
                    elif current_state == GAME_STATES['GAME_OVER']:
                        current_state = GAME_STATES['START']
        
        keys = pygame.key.get_pressed()
        
        if not items_in_zone:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                        score -= 5
                        combo = 0
                        penalty_text = regular_font.render("-5", True, UI_COLORS['WARNING'])
                        text_x = WIDTH//2 - penalty_text.get_width()//2
                        text_y = CATCH_ZONE_Y - 40
                        screen.blit(penalty_text, (text_x, text_y))
        
        for bag in falling_bags:
            if bag.rect.bottom > HEIGHT and not bag.caught:
                game_vars['missed_bags'] += 1
                game_vars['lives'] -= 1
                combo = 0
                bag.kill()
                
                if game_vars['lives'] <= 0:
                    current_state = GAME_STATES['GAME_OVER']
                    max_combo = max(max_combo, combo)
                    break
                
                continue
                
            if bag.rect.colliderect(pygame.Rect(0, CATCH_ZONE_Y, WIDTH, CATCH_ZONE_HEIGHT)):
                correct_key_pressed = (
                    (keys[pygame.K_LEFT] and bag.direction == 'LEFT') or
                    (keys[pygame.K_RIGHT] and bag.direction == 'RIGHT') or
                    (keys[pygame.K_UP] and bag.direction == 'UP') or
                    (keys[pygame.K_DOWN] and bag.direction == 'DOWN')
                )
                
                wrong_key_pressed = (
                    (keys[pygame.K_LEFT] and bag.direction != 'LEFT') or
                    (keys[pygame.K_RIGHT] and bag.direction != 'RIGHT') or
                    (keys[pygame.K_UP] and bag.direction != 'UP') or
                    (keys[pygame.K_DOWN] and bag.direction != 'DOWN')
                ) and any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], 
                         keys[pygame.K_UP], keys[pygame.K_DOWN]])

                if correct_key_pressed and not bag.wrong_key_pressed and not bag.caught:
                    points = bag.collect()
                    combo_multiplier = combo + 1
                    total_points = points * combo_multiplier
                    score += total_points
                    combo += 1





def draw_game_header(surface):
    header_height = 60
    draw_ui_panel(surface, 0, 0, WIDTH, header_height)
    
    title_bounce = abs(math.sin(pygame.time.get_ticks() * 0.003) * 3)
    title = title_font.render("✈️ SUITCASE HERO ✈️", True, UI_COLORS['ACCENT'])
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 10 + title_bounce))
    
    level_text = small_font.render(f"LEVEL {difficulty_level} ⭐", True, UI_COLORS['TEXT_SECONDARY'])
    surface.blit(level_text, (WIDTH - 150, 20))

def draw_game_screen(stats, belt_offset, messages):
    screen.fill(COLORS['BACKGROUND'])
    
    for y in range(0, CATCH_ZONE_HEIGHT, 20):
        belt_y = CATCH_ZONE_Y + y + belt_offset
        pygame.draw.line(screen, UI_COLORS['PANEL_BORDER'], 
            (0, belt_y), (WIDTH, belt_y), 3)
    
    belt_overlay = pygame.Surface((WIDTH, CATCH_ZONE_HEIGHT))
    belt_overlay.fill(UI_COLORS['PANEL_BG']) 
    belt_overlay.set_alpha(100)
    screen.blit(belt_overlay, (0, CATCH_ZONE_Y))
    
    pygame.draw.line(screen, UI_COLORS['PANEL_BORDER'], 
        (0, CATCH_ZONE_Y), (WIDTH, CATCH_ZONE_Y), 2)
    pygame.draw.line(screen, UI_COLORS['PANEL_BORDER'], 
        (0, HEIGHT - 1), (WIDTH, HEIGHT - 1), 2)
    
    draw_game_header(screen)
    draw_game_stats(screen, 20, 80, stats)
    
    all_sprites.draw(screen)
    
    if combo in messages:
        msg = messages[combo]
        text = regular_font.render(msg, True, UI_COLORS['ACCENT'])
        
        text_x = WIDTH//2 - text.get_width()//2
        text_y = HEIGHT//2 - 50
        bounce = abs(math.sin(pygame.time.get_ticks() * 0.005) * 10)
        
        bg = pygame.Surface((text.get_width() + 40, text.get_height() + 20))
        bg.fill(UI_COLORS['PANEL_BG'])
        bg.set_alpha(200)
        
        screen.blit(bg, (text_x - 20, text_y + bounce - 10))
        screen.blit(text, (text_x, text_y + bounce))

def draw_start_screen():
    screen.fill(COLORS['BACKGROUND'])
    
    panel_width = 600
    panel_height = 400
    panel_x = WIDTH//2 - panel_width//2
    panel_y = HEIGHT//2 - panel_height//2
    draw_ui_panel(screen, panel_x, panel_y, panel_width, panel_height)
    
    title = title_font.render("SUITCASE HERO", True, UI_COLORS['ACCENT'])
    screen.blit(title, (WIDTH//2 - title.get_width()//2, panel_y + 40))
    
    instructions = [
        "Match the arrow keys with the suitcase directions",
        "Catch them on the conveyor belt",
        "Get bonus points for lunch boxes!",
        "Don't let too many suitcases fall",
        "",
        "Press SPACE to start!"
    ]
    
    for i, text in enumerate(instructions):
        color = UI_COLORS['ACCENT'] if i == len(instructions)-1 else UI_COLORS['TEXT_PRIMARY']
        instruction = regular_font.render(text, True, color)
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, panel_y + 150 + i * 40))

def draw_game_over_screen():
    draw_ui_panel(screen, WIDTH//2 - 250, HEIGHT//2 - 150, 500, 300, COLORS['WRONG_KEY'])
    
    game_over = title_font.render("GAME OVER!", True, WHITE)
    screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, HEIGHT//2 - 100))
    
    score_text = regular_font.render(f"Final Score: {score}", True, COLORS['UI_GOLD'])
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    
    combo_text = regular_font.render(f"Max Combo: {max_combo}", True, COLORS['UI_GOLD'])
    screen.blit(combo_text, (WIDTH//2 - combo_text.get_width()//2, HEIGHT//2 + 40))
    
    diff_text = regular_font.render(f"Difficulty Reached: {difficulty_level}", True, COLORS['UI_GOLD'])
    screen.blit(diff_text, (WIDTH//2 - diff_text.get_width()//2, HEIGHT//2 + 80))
    
    restart = regular_font.render("Press SPACE to play again! 🎮", True, UI_COLORS['SUCCESS'])
    quit_text = regular_font.render("Press ESC to quit ❌", True, UI_COLORS['WARNING'])
    screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 140))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 180))

def run_game():
    global score, combo, max_combo, difficulty_level

    game_clock = pygame.time.Clock()
    running = True
    current_state = GAME_STATES['START']
    best_combo = 0
    belt_offset = 0
    items_in_zone = False

    combo_texts = {
        5: "HIGH FIVE! 🎒",
        10: "SUPER STAR! ⭐", 
        15: "AMAZING! 🌟",
        20: "INCREDIBLE! 🏆",
        25: "LEGENDARY! 👑"
    }

    def reset_game():
        global score, combo, difficulty_level
        score = 0
        combo = 0
        difficulty_level = 1
        all_sprites.empty()
        falling_bags.empty()
        return {
            'spawn_timer': 0,
            'spawn_times': [BASE_SPAWN_INTERVAL],
            'speed_multiplier': 1.0,
            'difficulty_level': 1,
            'last_difficulty_increase': 0,
            'missed_bags': 0,
            'lives': 3
        }

    game_vars = reset_game()

    while running:
        events = pygame.event.get()
        
        screen.fill(COLORS['BACKGROUND'])

        items_in_zone = False
        for bag in falling_bags:
            if bag.rect.colliderect(pygame.Rect(0, CATCH_ZONE_Y, WIDTH, CATCH_ZONE_HEIGHT)):
                items_in_zone = True
                break
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if current_state == GAME_STATES['START']:
                        current_state = GAME_STATES['PLAYING']
                        game_vars = reset_game()
                    elif current_state == GAME_STATES['GAME_OVER']:
                        current_state = GAME_STATES['START']
        
        keys = pygame.key.get_pressed()
        
        if not items_in_zone:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                        score -= 5
                        combo = 0
                        penalty_text = regular_font.render("-5", True, UI_COLORS['WARNING'])
                        text_x = WIDTH//2 - penalty_text.get_width()//2
                        text_y = CATCH_ZONE_Y - 40
                        screen.blit(penalty_text, (text_x, text_y))
        
        for bag in falling_bags:
            if bag.rect.bottom > HEIGHT and not bag.caught:
                game_vars['missed_bags'] += 1
                game_vars['lives'] -= 1
                combo = 0
                bag.kill()
                
                if game_vars['lives'] <= 0:
                    current_state = GAME_STATES['GAME_OVER']
                    max_combo = max(max_combo, combo)
                    break
                
                continue
                
            if bag.rect.colliderect(pygame.Rect(0, CATCH_ZONE_Y, WIDTH, CATCH_ZONE_HEIGHT)):
                correct_key_pressed = (
                    (keys[pygame.K_LEFT] and bag.direction == 'LEFT') or
                    (keys[pygame.K_RIGHT] and bag.direction == 'RIGHT') or
                    (keys[pygame.K_UP] and bag.direction == 'UP') or
                    (keys[pygame.K_DOWN] and bag.direction == 'DOWN')
                )
                
                wrong_key_pressed = (
                    (keys[pygame.K_LEFT] and bag.direction != 'LEFT') or
                    (keys[pygame.K_RIGHT] and bag.direction != 'RIGHT') or
                    (keys[pygame.K_UP] and bag.direction != 'UP') or
                    (keys[pygame.K_DOWN] and bag.direction != 'DOWN')
                ) and any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]])

                if correct_key_pressed and not bag.wrong_key_pressed and not bag.caught:
                    points = bag.collect()
                    combo_multiplier = combo + 1
                    total_points = points * combo_multiplier
                    score += total_points
                    combo += 1
                    bag.caught = True
                    
                    points_text = f"+{total_points}"
                    combo_text = f"COMBO {combo}!"
                    
                    combo_message = combo_texts.get(combo)
                    if combo_message:
                        combo_text = combo_message
                    
                    points_surface = regular_font.render(points_text, True, UI_COLORS['SUCCESS'])
                    combo_surface = small_font.render(combo_text, True, UI_COLORS['SUCCESS'])
                    
                    screen.blit(points_surface, (bag.rect.x + bag.rect.width//2, bag.rect.y - 30))
                    screen.blit(combo_surface, (bag.rect.x + bag.rect.width//2, bag.rect.y - 10))
                
                if wrong_key_pressed and not bag.caught:
                    bag.wrong_key_pressed = True
                    score -= 5
                    combo = 0
                    penalty_text = regular_font.render("-5", True, UI_COLORS['WARNING'])
                    text_x = WIDTH//2 - penalty_text.get_width()//2
                    text_y = CATCH_ZONE_Y - 40
                    screen.blit(penalty_text, (text_x, text_y))
        
        if current_state == GAME_STATES['PLAYING']:
            if score < -1000 or game_vars['lives'] <= 0:
                current_state = GAME_STATES['GAME_OVER']
                max_combo = max(max_combo, combo)

        if current_state == GAME_STATES['START']:
            draw_start_screen()
        
        elif current_state == GAME_STATES['GAME_OVER']:
            draw_game_over_screen()
        
        elif current_state == GAME_STATES['PLAYING']:
            if score >= game_vars['last_difficulty_increase'] + DIFFICULTY_INCREASE_THRESHOLD:
                game_vars['difficulty_level'] += 1
                difficulty_level = game_vars['difficulty_level']
                game_vars['speed_multiplier'] *= SPEED_INCREASE_RATE
                game_vars['last_difficulty_increase'] = score

            game_vars['spawn_timer'] = (game_vars['spawn_timer'] + 1) % (max(game_vars['spawn_times']) + 1)

            if game_vars['spawn_timer'] in game_vars['spawn_times']:
                weights = [
                    max(10, 50 - game_vars['difficulty_level'] * 5),
                    max(10, 40 - game_vars['difficulty_level'] * 3),
                    min(40, 20 + game_vars['difficulty_level'] * 2),
                    min(20, 8 + game_vars['difficulty_level']),
                    min(10, 2 + game_vars['difficulty_level'])
                ]
                
                bag_type = random.choices(list(LUGGAGE_TYPES.values()), 
                                        weights=weights)[0]
                x_pos = random.randint(100, WIDTH - 100)
                new_bag = FallingBag(x_pos, -SUITCASE_DIM[1], bag_type, game_vars['speed_multiplier'])
                all_sprites.add(new_bag)
                falling_bags.add(new_bag)

            all_sprites.update()
            
            draw_game_screen(game_vars, belt_offset, combo_texts)

            items_in_zone = False
            for bag in falling_bags:
                if bag.rect.colliderect(pygame.Rect(0, CATCH_ZONE_Y, WIDTH, CATCH_ZONE_HEIGHT)):
                    items_in_zone = True
                    break
            
            catch_zone_color = CATCH_ZONE_ACTIVE_COLOR if items_in_zone else CATCH_ZONE_INACTIVE_COLOR
            pygame.draw.rect(screen, catch_zone_color, 
                            (0, CATCH_ZONE_Y, WIDTH, CATCH_ZONE_HEIGHT))
            
            border_color = UI_COLORS['SUCCESS'] if items_in_zone else COLORS['UI_BLUE']
            border_width = 6 if items_in_zone else 4
            pygame.draw.line(screen, border_color, 
                            (0, CATCH_ZONE_Y), (WIDTH, CATCH_ZONE_Y), border_width)
            pygame.draw.line(screen, border_color, 
                            (0, HEIGHT - 1), (WIDTH, HEIGHT - 1), border_width)

            if items_in_zone:
                catch_text = regular_font.render("CATCH NOW! 🎯", True, UI_COLORS['SUCCESS'])
                text_x = WIDTH - catch_text.get_width() - 20
                text_y = CATCH_ZONE_Y - 40
                text_y += abs(math.sin(pygame.time.get_ticks() * 0.005) * 5)
                catch_text.set_alpha(255)
                screen.blit(catch_text, (text_x, text_y))

            if game_vars['spawn_timer'] < 100:
                instruction_panel = pygame.Surface((600, 40))
                instruction_panel.fill(COLORS['UI_BLUE'])
                instruction_panel.set_alpha(200)
                screen.blit(instruction_panel, (WIDTH//2 - 300, HEIGHT - 150))
                                       
                instruction_text = small_font.render(
                    "← → ↑ ↓  Match arrows on luggage when they reach the conveyor!", 
                    True, WHITE)
                screen.blit(instruction_text, (WIDTH//2 - 290, HEIGHT - 140))

        pygame.display.flip()
        game_clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    run_game()
