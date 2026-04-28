import pygame
import sys
import random
import os
import json
from datetime import datetime

# --- 1. INITIALISATIE ---
pygame.init()
pygame.font.init() # Expliciet font initialiseren voor de zekerheid 

# --- CONFIGURATIE & CONSTANTEN ---
WIDTH, HEIGHT = 300, 600
COLS, ROWS = 10, 20
CELL_SIZE = WIDTH // COLS
SIDEBAR_WIDTH = 150
TOTAL_WIDTH = WIDTH + SIDEBAR_WIDTH

BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Lettertypes laden
FONT_UI = pygame.font.SysFont('Arial', 24, bold=True)

# Tetromino definities
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

COLORS = {
    'I': (0, 200, 200), 'O': (200, 200, 0), 'T': (150, 0, 150),
    'S': (0, 200, 0), 'Z': (200, 0, 0), 'J': (0, 0, 200), 'L': (200, 100, 0)
}

# --- FUNCTIES ---

def get_new_piece():
    shape_type = random.choice(list(SHAPES.keys()))
    return {
        'matrix': SHAPES[shape_type],
        'color': COLORS[shape_type],
        'x': COLS // 2 - len(SHAPES[shape_type][0]) // 2,
        'y': 0
    }

def is_valid_move(piece_matrix, grid, x_pos, y_pos):
    for y, row in enumerate(piece_matrix):
        for x, cell in enumerate(row):
            if cell:
                new_x = x_pos + x
                new_y = y_pos + y
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False
                if new_y >= 0 and grid[new_y][new_x]:
                    return False
    return True

def lock_piece(piece, grid):
    for y, row in enumerate(piece['matrix']):
        for x, cell in enumerate(row):
            if cell:
                grid[piece['y'] + y][piece['x'] + x] = piece['color']

def clear_rows(grid):
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    rows_cleared = ROWS - len(new_grid)
    for _ in range(rows_cleared):
        new_grid.insert(0, [None for _ in range(COLS)])
    return new_grid, rows_cleared

def rotate(matrix):
    return [list(row) for row in zip(*matrix[::-1])]

def draw_game(screen, grid, current_piece, next_piece):
    screen.fill(BLACK)
    # Grid lijnen
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, DARK_GREY, rect, 1)
    
    # Sidebar
    pygame.draw.rect(screen, (20, 20, 20), (WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
    
    # Grid blokjes
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            if color:
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))
    
    # Actieve piece
    for y, row in enumerate(current_piece['matrix']):
        for x, cell in enumerate(row):
            if cell:
                px = (current_piece['x'] + x) * CELL_SIZE
                py = (current_piece['y'] + y) * CELL_SIZE
                pygame.draw.rect(screen, current_piece['color'], (px, py, CELL_SIZE - 1, CELL_SIZE - 1))
    
    # Preview
    text = FONT_UI.render('NEXT', True, WHITE)
    screen.blit(text, (WIDTH + 20, 20))
    for y, row in enumerate(next_piece['matrix']):
        for x, cell in enumerate(row):
            if cell:
                px = WIDTH + 30 + (x * CELL_SIZE)
                py = 70 + (y * CELL_SIZE)
                pygame.draw.rect(screen, next_piece['color'], (px, py, CELL_SIZE - 1, CELL_SIZE - 1))

def draw_score(screen, score, level):
    # Score weergeven
    label = FONT_UI.render('SCORE', True, WHITE)
    screen.blit(label, (WIDTH + 20, 200))
    val = FONT_UI.render(str(score), True, GREEN)
    screen.blit(val, (WIDTH + 20, 230))

    # Level weergeven
    label = FONT_UI.render('LEVEL', True, WHITE)
    screen.blit(label, (WIDTH + 20, 300))
    val = FONT_UI.render(str(level), True, GREEN)
    screen.blit(val, (WIDTH + 20, 330))

def draw_game_over(screen, final_score, highscores):
    overlay = pygame.Surface((TOTAL_WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 230)) 
    screen.blit(overlay, (0, 0))
    
    msg = pygame.font.SysFont('Arial', 40, bold=True).render('HALL OF FAME', True, YELLOW)
    screen.blit(msg, (TOTAL_WIDTH // 2 - msg.get_width() // 2, 30))
    
    # Header voor kolommen
    header_txt = pygame.font.SysFont('Arial', 18, bold=True).render("NAME      SCORE      DATE", True, WHITE)
    screen.blit(header_txt, (30, 90))
    
    for i, entry in enumerate(highscores):
        # Markeer de huidige score in het groen
        color = GREEN if entry["score"] == final_score else WHITE
        
        # Format: Naam links, Score midden, Datum rechts
        name_txt = f"{i+1}. {entry['name']}"
        score_txt = str(entry['score'])
        date_txt = entry['date']
        
        # Teken de tekst (je kunt hier met x-posities spelen voor mooie kolommen)
        screen.blit(FONT_UI.render(name_txt, True, color), (30, 120 + i * 30))
        screen.blit(FONT_UI.render(score_txt, True, color), (160, 120 + i * 30))
        screen.blit(pygame.font.SysFont('Arial', 16).render(date_txt, True, color), (250, 125 + i * 30))

    # Instructies
    retry_txt = FONT_UI.render("Press 'R' to Restart", True, WHITE)
    quit_txt = FONT_UI.render("Press 'Q' to Quit", True, WHITE)
    screen.blit(retry_txt, retry_txt.get_rect(center=(TOTAL_WIDTH // 2, HEIGHT - 80)))
    screen.blit(quit_txt, quit_txt.get_rect(center=(TOTAL_WIDTH // 2, HEIGHT - 40)))

def init_audio():
    """Initialiseert de mixer en laadt audiobestanden veilig in."""
    pygame.mixer.init()
    
    # Om te zorgen dat dit script ook werkt wanneer het is verpakt met PyInstaller, 
    # moeten we de paden naar de audiobestanden correct beheren.
    try:
        # PyInstaller maakt een tijdelijke map aan en slaat het pad op in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    music_file = "tetris.mp3"
    sound_file = "clear.wav"

    music_file = os.path.join(base_path, music_file)
    sound_file = os.path.join(base_path, sound_file)    
    
    # Achtergrondmuziek laden
    if os.path.exists(music_file):
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1) # -1 = oneindig loopen
            pygame.mixer.music.set_volume(0.3)
        except pygame.error as e:
            print(f"Kon muziek niet afspelen: {e}")
    else:
        print("Muziekbestand niet gevonden. Spel start in stilte.")

    # Geluidseffect laden
    clear_sfx = None
    if os.path.exists(sound_file):
        try:
            clear_sfx = pygame.mixer.Sound(sound_file)
            clear_sfx.set_volume(0.5)
        except pygame.error as e:
            print(f"Kon geluidseffect niet laden: {e}")
            
    return clear_sfx

# --- HIGHSCORE MANAGEMENT ---
# Deze functies beheren het laden, opslaan en bijwerken van highscores in een JSON-bestand.

# Bij het behalen van een nieuwe highscore, wordt de speler gevraagd om zijn naam in te voeren. 
# De highscores worden opgeslagen als een lijst van dictionaries met 'name', 'score' en 'date' velden.
# we moeten dit zo doen omdat pygame geen standaard tekstveld krijgt, 
# dus we simuleren dit met een eenvoudige loop die invoer accepteert.
def get_player_name(screen):
    name = ""
    asking = True
    while asking:
        screen.fill(BLACK)
        # Teken een simpel tekstveld-scherm
        prompt = FONT_UI.render("Nieuwe Highscore! Typ je naam:", True, WHITE)
        name_surface = FONT_UI.render(name + "_", True, YELLOW)
        
        screen.blit(prompt, (TOTAL_WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(name_surface, (TOTAL_WIDTH // 2 - name_surface.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name != "":
                    asking = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    # Voeg alleen letters/cijfers toe en hou het kort
                    if len(name) < 10 and event.unicode.isalnum():
                        name += event.unicode
    return name

def load_highscores():
    if os.path.exists('highscores.json'):
        with open('highscores.json', 'r') as f:
            return json.load(f)
    return []

def save_highscores(scores):
    with open('highscores.json', 'w') as f:
        json.dump(scores, f)

def update_highscores(new_score, player_name=None):
    scores = load_highscores()
    current_time = datetime.now().strftime("%Y-%m-%d")

    new_entry = {
        "name": player_name,
        "score": new_score,
        "date": current_time
    }

    scores.append(new_entry)
    scores.sort(key=lambda x: x['score'], reverse=True)  # Sorteer op score, hoogste eerst
    scores = scores[:10]  # Behou alleen de top 10
    save_highscores(scores)
    return scores

def handle_player_input(current_piece, grid):
    """Verwerkt toetsenbord-input en geeft de gewenste valsnelheid terug."""
    speed = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT", None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN: speed = "FAST"
            if event.key == pygame.K_LEFT:
                if is_valid_move(current_piece['matrix'], grid, current_piece['x'] - 1, current_piece['y']):
                    current_piece['x'] -= 1
            if event.key == pygame.K_RIGHT:
                if is_valid_move(current_piece['matrix'], grid, current_piece['x'] + 1, current_piece['y']):
                    current_piece['x'] += 1
            if event.key == pygame.K_UP:
                rotated = rotate(current_piece['matrix'])
                if is_valid_move(rotated, grid, current_piece['x'], current_piece['y']):
                    current_piece['matrix'] = rotated
        
        if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
            speed = "NORMAL"
            
    return "CONTINUE", speed

def update_game_physics(current_piece, next_piece, grid, score, level, lines_total, clear_sound):
    """Berekent wat er gebeurt als een blokje valt of vast komt te zitten."""
    game_over = False
    
    if is_valid_move(current_piece['matrix'], grid, current_piece['x'], current_piece['y'] + 1):
        current_piece['y'] += 1
    else:
        lock_piece(current_piece, grid)
        grid, removed = clear_rows(grid)
        
        if removed > 0:
            if clear_sound: clear_sound.play()
            score += {1: 100, 2: 300, 3: 500, 4: 800}.get(removed, 0)
            lines_total += removed
            level = (lines_total // 10) + 1
            
        current_piece = next_piece
        next_piece = get_new_piece()
        
        if not is_valid_move(current_piece['matrix'], grid, current_piece['x'], current_piece['y']):
            game_over = True
            
    return current_piece, next_piece, grid, score, level, lines_total, game_over

def manage_game_over(screen, score, highscore_saved, highscores_list):
    """Regelt de naam-input en het opslaan van de score zodra het spel stopt."""
    if not highscore_saved:
        pygame.mixer.music.stop()
        player_name = get_player_name(screen)
        highscores_list = update_highscores(score, player_name)
        highscore_saved = True
    
    # Check voor herstart/afsluiten via toetsenbord
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, True, highscores_list # running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return "RESTART", highscore_saved, highscores_list
            if event.key == pygame.K_q:
                return False, True, highscores_list # running = False
                
    return True, highscore_saved, highscores_list # running = True

# --- MAIN ENGINE ---

def main():
    screen = pygame.display.set_mode((TOTAL_WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris - Frank's Versie")
    clock = pygame.time.Clock()

    clear_sound = init_audio() 

    # Variabelen initialiseren
    fall_time = 0
    normal_speed = 500
    fast_speed = 50
    current_fall_speed = normal_speed
    score = 0
    game_over = False
    level = 1
    lines_total = 0  # <--- Veranderd van lines_cleared_total naar lines_total

    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    current_piece = get_new_piece()
    next_piece = get_new_piece()

    highscore_saved = False 
    highscores_list = load_highscores() 
    
    running = True
    while running:
        dt = clock.tick(60)

        if game_over:
            # 2. Game Over Flow (Naam invoeren & Highscores)
            status, highscore_saved, highscores_list = manage_game_over(screen, score, highscore_saved, highscores_list)
            if status == "RESTART": 
                main()
                return
            if status == False: 
                running = False
        else:
            # 3. Physics & Input
            fall_time += dt
            status, speed_change = handle_player_input(current_piece, grid)
            
            if status == "QUIT": 
                running = False
            
            # Snelheid aanpassen op basis van input
            if speed_change == "FAST": 
                current_fall_speed = fast_speed
            elif speed_change == "NORMAL": 
                current_fall_speed = max(100, 500 - (level - 1) * 50)

            # Zwaartekracht update
            if fall_time > current_fall_speed:
                # Hier gebruiken we nu overal 'lines_total'
                current_piece, next_piece, grid, score, level, lines_total, game_over = update_game_physics(
                    current_piece, next_piece, grid, score, level, lines_total, clear_sound
                )
                fall_time = 0

        # --- RENDERING ---
        draw_game(screen, grid, current_piece, next_piece)
        draw_score(screen, score, level)

        if game_over:
            draw_game_over(screen, score, highscores_list)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()