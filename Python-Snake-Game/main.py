"""
Main game file for Snake Game
Handles game loop, events, rendering, and menu system
"""

import pygame
import sys
import os
import random
from snake import Snake
from food import Food
from word_socket import WordCommandClient, DIRECTION_WORDS, START_WORDS, STOP_WORDS
from config import *

# Keyboard arrow keys mapped to direction tuples (for input + visualization)
ARROW_KEY_DIRECTIONS = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}


class Button:
    """
    Button class for menu interactions.
    """
    
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        """
        Initialize a button.
        
        Args:
            x (int): X-coordinate
            y (int): Y-coordinate
            width (int): Button width
            height (int): Button height
            text (str): Button text
            color (tuple): Normal color
            hover_color (tuple): Hover color
            text_color (tuple): Text color
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def draw(self, surface, font):
        """
        Draw the button on the surface.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            font (pygame.font.Font): Font to use
        """
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)
        
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, mouse_pos):
        """
        Check if mouse is hovering over button.
        
        Args:
            mouse_pos (tuple): Mouse position
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def is_clicked(self, mouse_pos, mouse_clicked):
        """
        Check if button is clicked.
        
        Args:
            mouse_pos (tuple): Mouse position
            mouse_clicked (bool): Mouse button state
        
        Returns:
            bool: True if clicked
        """
        return self.is_hovered and mouse_clicked


class SoundManager:
    """Lightweight sound manager (optional). Tries to load .wav files if present."""
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            pygame.mixer.init()
            self.enabled = True
            # Load sounds if files exist (place optional wavs in project root)
            for name, filename in {
                'eat': 'eat.wav',
                'gameover': 'gameover.wav',
                'click': 'click.wav',
            }.items():
                if os.path.exists(filename):
                    self.sounds[name] = pygame.mixer.Sound(filename)
        except Exception:
            self.enabled = False

    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass


class Game:
    """
    Main game class that controls the game flow.
    """

    def __init__(self):
        """
        Initialize the game with pygame and game objects.
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            pygame.display.set_caption(WINDOW_TITLE)
            self.clock = pygame.time.Clock()

            # The game is always rendered at the base resolution and then
            # scaled to the actual window size (keeping the aspect ratio),
            # so resizing the window scales every element uniformly.
            self.base_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
            self.game_surface = pygame.Surface(self.base_size)
            self.scale = 1.0
            self.offset = (0, 0)
            
            # Game states
            self.state = "MENU"  # MENU, SETTINGS, PLAYING, GAME_OVER
            self.difficulty = DEFAULT_DIFFICULTY
            self.speed = DIFFICULTY_LEVELS[self.difficulty]
            self.move_timer = 0
            self.move_delay = 1000 // self.speed  # milliseconds between moves
            self.wrap_around = WRAP_AROUND_DEFAULT
            self.obstacles_enabled = OBSTACLES_DEFAULT
            self.obstacles = set()
            self.theme_name = DEFAULT_THEME
            self.bg_color = THEMES[self.theme_name]['bg']
            self.grid_color = THEMES[self.theme_name]['grid']
            self.sound = SoundManager()
            # Voice command socket (KWS word socket, see socket_docs.md)
            self.voice_client = WordCommandClient()
            self.voice_client.start()
            # Bonus food state
            self.bonus_pos = None
            self.bonus_expire_at = 0
            # Input visualization: last time each direction input was seen
            self.input_flash = {UP: 0, DOWN: 0, LEFT: 0, RIGHT: 0}
            self.last_input_word = None
            self.last_input_time = 0
            
            # Initialize game objects
            self.snake = None
            self.food = None
            self.score = 0
            self.high_score = self.load_high_score()
            self.paused = False
            
            # Apply initial theme colors
            self.apply_theme(self.theme_name)

            # Create menu buttons
            self.create_menu_buttons()
            
        except Exception as e:
            print(f"Error initializing game: {e}")
            sys.exit(1)

    def create_menu_buttons(self):
        """
        Create buttons for menus.
        """
        center_x = WINDOW_WIDTH // 2
        
        # Main menu buttons
        self.start_button = Button(center_x - 100, 250, 200, 50, "START GAME", DARK_GREEN, GREEN)
        self.settings_button = Button(center_x - 100, 320, 200, 50, "SETTINGS", DARK_GRAY, GRAY)
        self.quit_button = Button(center_x - 100, 390, 200, 50, "QUIT", RED, ORANGE)
        
        # Settings buttons
        self.difficulty_buttons = {}
        y_offset = 200
        for i, (diff_name, speed) in enumerate(DIFFICULTY_LEVELS.items()):
            self.difficulty_buttons[diff_name] = Button(
                center_x - 120, y_offset + i * 70, 240, 50,
                f"{diff_name} ({speed} moves/sec)", DARK_GRAY, GRAY
            )
        # Toggles and theme
        self.wrap_button = Button(center_x - 140, 430, 280, 45, "WRAP AROUND: OFF", DARK_GRAY, GRAY)
        self.obstacles_button = Button(center_x - 140, 480, 280, 45, "OBSTACLES: OFF", DARK_GRAY, GRAY)
        self.theme_button = Button(center_x - 140, 530, 280, 45, f"THEME: {self.theme_name}", DARK_GRAY, GRAY)
        self.back_button = Button(center_x - 100, 585, 200, 45, "BACK", DARK_GRAY, GRAY)
        
        # Game over buttons
        self.restart_button = Button(center_x - 100, 320, 200, 50, "RESTART", DARK_GREEN, GREEN)
        self.menu_button = Button(center_x - 100, 390, 200, 50, "MAIN MENU", DARK_GRAY, GRAY)

    def layout_settings(self):
        """Compute layout for settings controls to avoid overlap and fit the screen."""
        center_x = WINDOW_WIDTH // 2
        # Difficulty buttons stacked vertically
        diff_w, diff_h = 240, 50
        start_y = 180
        spacing = 12
        for i, diff_name in enumerate(DIFFICULTY_LEVELS.keys()):
            btn = self.difficulty_buttons[diff_name]
            btn.rect.width = diff_w
            btn.rect.height = diff_h
            btn.rect.x = center_x - diff_w // 2
            btn.rect.y = start_y + i * (diff_h + spacing)

        # Toggles in a single row (3 columns)
        toggle_w, toggle_h, gap = 220, 45, 20
        total_w = 3 * toggle_w + 2 * gap
        left = center_x - total_w // 2
        toggles_y = start_y + len(DIFFICULTY_LEVELS) * (diff_h + spacing) + 24

        self.wrap_button.rect.width = toggle_w
        self.wrap_button.rect.height = toggle_h
        self.wrap_button.rect.x = left
        self.wrap_button.rect.y = toggles_y

        self.obstacles_button.rect.width = toggle_w
        self.obstacles_button.rect.height = toggle_h
        self.obstacles_button.rect.x = left + toggle_w + gap
        self.obstacles_button.rect.y = toggles_y

        self.theme_button.rect.width = toggle_w
        self.theme_button.rect.height = toggle_h
        self.theme_button.rect.x = left + 2 * (toggle_w + gap)
        self.theme_button.rect.y = toggles_y

        # Back button near bottom with margin
        self.back_button.rect.width = 200
        self.back_button.rect.height = 45
        self.back_button.rect.x = center_x - 100
        self.back_button.rect.y = WINDOW_HEIGHT - 70

    def window_to_game(self, pos):
        """
        Convert window coordinates to base-resolution game coordinates.

        Args:
            pos (tuple): Mouse position in window coordinates

        Returns:
            tuple: Position on the base-resolution game surface
        """
        wx, wy = pos
        gx = (wx - self.offset[0]) / self.scale
        gy = (wy - self.offset[1]) / self.scale
        return (int(gx), int(gy))

    def load_high_score(self):
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r') as f:
                    return int(f.read().strip() or 0)
        except Exception:
            pass
        return 0

    def save_high_score(self):
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    def apply_theme(self, theme_name):
        theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
        self.bg_color = theme['bg']
        self.grid_color = theme['grid']
        Snake.set_colors(theme['snake'], theme['snake_head'])
        if self.food:
            self.food.set_color(theme['food'])

    def reset_game(self):
        """
        Reset the game to initial state.
        """
        # Calculate starting position (center of the play area)
        start_x = PLAY_LEFT + (PLAY_WIDTH // 2 // GRID_SIZE) * GRID_SIZE
        start_y = PLAY_TOP + (PLAY_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE
        
        self.snake = Snake(start_x, start_y)
        self.food = Food(PLAY_WIDTH, PLAY_HEIGHT, PLAY_OFFSET)
        # Apply theme to food
        self.apply_theme(self.theme_name)
        
        # Generate obstacles if enabled
        self.obstacles = set()
        if self.obstacles_enabled:
            self.generate_obstacles()
        
        # Ensure food doesn't spawn on snake or obstacles
        avoid = list(self.snake.body) + list(self.obstacles)
        self.food.spawn(avoid_positions=avoid)
        
        self.score = 0
        self.paused = False
        self.move_timer = 0
        self.state = "PLAYING"
        # Clear any bonus food
        self.bonus_pos = None
        self.bonus_expire_at = 0

    def generate_obstacles(self):
        """Create random obstacle blocks on the grid, avoiding snake start and food."""
        grid_w = PLAY_WIDTH // GRID_SIZE
        grid_h = PLAY_HEIGHT // GRID_SIZE
        forbidden = set(self.snake.body)
        # leave a radius around the snake head
        head = self.snake.get_head_position()
        forbidden.update({(head[0] + dx * GRID_SIZE, head[1] + dy * GRID_SIZE)
                          for dx in range(-2, 3) for dy in range(-2, 3)})

        # Avoid current food pos too
        forbidden.add(self.food.get_position())
        attempts = 0
        while len(self.obstacles) < OBSTACLE_COUNT and attempts < OBSTACLE_COUNT * 20:
            attempts += 1
            x = PLAY_LEFT + random.randint(0, grid_w - 1) * GRID_SIZE
            y = PLAY_TOP + random.randint(0, grid_h - 1) * GRID_SIZE
            pos = (x, y)
            if pos not in forbidden:
                self.obstacles.add(pos)

    def register_input(self, direction, word=None):
        """
        Record an incoming direction input so the on-screen arrow pad lights up.

        Args:
            direction (tuple): Direction tuple (dx, dy) matching UP/DOWN/LEFT/RIGHT
            word (str, optional): The raw input word (e.g. a voice command label)
        """
        now = pygame.time.get_ticks()
        if direction in self.input_flash:
            self.input_flash[direction] = now
        self.last_input_word = word if word is not None else self.last_input_word
        self.last_input_time = now

    def handle_events(self):
        """
        Handle keyboard and mouse events.
        
        Returns:
            bool: False if quit event detected, True otherwise
        """
        mouse_pos = self.window_to_game(pygame.mouse.get_pos())
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # VIDEORESIZE events need no handling: draw() reads the actual
            # window size every frame and scales the content to fit. We must
            # NOT call set_mode() here -- that would interrupt the drag.
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True
            
            if event.type == pygame.KEYDOWN:
                # Menu navigation
                if self.state == "MENU":
                    if event.key == pygame.K_ESCAPE:
                        return False
                
                # Settings navigation
                elif self.state == "SETTINGS":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                
                # Game over navigation
                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                
                # Playing controls
                elif self.state == "PLAYING":
                    direction = ARROW_KEY_DIRECTIONS.get(event.key)
                    if direction is not None:
                        self.register_input(direction)
                        if not self.paused:
                            self.snake.change_direction(direction)
                    elif not self.paused:
                        if event.key == pygame.K_p:
                            self.paused = True
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "MENU"
                    else:
                        if event.key == pygame.K_p:
                            self.paused = False
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "MENU"
        
        # Handle menu button clicks
        if self.state == "MENU":
            self.handle_menu_clicks(mouse_pos, mouse_clicked)
        elif self.state == "SETTINGS":
            self.handle_settings_clicks(mouse_pos, mouse_clicked)
        elif self.state == "GAME_OVER":
            self.handle_game_over_clicks(mouse_pos, mouse_clicked)
        
        return True
    
    def handle_word_commands(self):
        """
        Process voice commands received from the KWS word socket.

        Direction words (left/right/up/down) steer the snake while playing;
        "go" starts/resumes/restarts the game and "stop" pauses it.
        """
        word = self.voice_client.get_command()
        while word is not None:
            if word in DIRECTION_WORDS:
                direction = DIRECTION_WORDS[word]
                # Always show the incoming voice command on the arrow pad
                self.register_input(direction, word)
                if self.state == "PLAYING" and not self.paused:
                    self.snake.change_direction(direction)
            elif word in START_WORDS:
                if self.state in ("MENU", "GAME_OVER"):
                    self.reset_game()
                elif self.state == "PLAYING" and self.paused:
                    self.paused = False
            elif word in STOP_WORDS:
                if self.state == "PLAYING" and not self.paused:
                    self.paused = True
            word = self.voice_client.get_command()

    def handle_menu_clicks(self, mouse_pos, mouse_clicked):
        """
        Handle main menu button clicks.
        
        Args:
            mouse_pos (tuple): Mouse position
            mouse_clicked (bool): Mouse click state
        """
        self.start_button.check_hover(mouse_pos)
        self.settings_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)
        
        if self.start_button.is_clicked(mouse_pos, mouse_clicked):
            self.sound.play('click')
            self.reset_game()
        elif self.settings_button.is_clicked(mouse_pos, mouse_clicked):
            self.sound.play('click')
            self.state = "SETTINGS"
        elif self.quit_button.is_clicked(mouse_pos, mouse_clicked):
            self.sound.play('click')
            self.voice_client.stop()
            pygame.quit()
            sys.exit()
    
    def handle_settings_clicks(self, mouse_pos, mouse_clicked):
        """
        Handle settings menu button clicks.
        
        Args:
            mouse_pos (tuple): Mouse position
            mouse_clicked (bool): Mouse click state
        """
        # Ensure button rects match current layout before hit testing
        self.layout_settings()
        for diff_name, button in self.difficulty_buttons.items():
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                self.difficulty = diff_name
                self.speed = DIFFICULTY_LEVELS[diff_name]
                self.move_delay = 1000 // self.speed
                self.sound.play('click')
        
        # Wrap toggle
        self.wrap_button.check_hover(mouse_pos)
        if self.wrap_button.is_clicked(mouse_pos, mouse_clicked):
            self.wrap_around = not self.wrap_around
            self.sound.play('click')

        # Obstacles toggle
        self.obstacles_button.check_hover(mouse_pos)
        if self.obstacles_button.is_clicked(mouse_pos, mouse_clicked):
            self.obstacles_enabled = not self.obstacles_enabled
            self.sound.play('click')

        # Theme cycle
        self.theme_button.check_hover(mouse_pos)
        if self.theme_button.is_clicked(mouse_pos, mouse_clicked):
            theme_names = list(THEMES.keys())
            idx = theme_names.index(self.theme_name)
            self.theme_name = theme_names[(idx + 1) % len(theme_names)]
            self.apply_theme(self.theme_name)
            self.sound.play('click')

        self.back_button.check_hover(mouse_pos)
        if self.back_button.is_clicked(mouse_pos, mouse_clicked):
            self.state = "MENU"
    
    def handle_game_over_clicks(self, mouse_pos, mouse_clicked):
        """
        Handle game over menu button clicks.
        
        Args:
            mouse_pos (tuple): Mouse position
            mouse_clicked (bool): Mouse click state
        """
        self.restart_button.check_hover(mouse_pos)
        self.menu_button.check_hover(mouse_pos)
        
        if self.restart_button.is_clicked(mouse_pos, mouse_clicked):
            self.sound.play('click')
            self.reset_game()
        elif self.menu_button.is_clicked(mouse_pos, mouse_clicked):
            self.sound.play('click')
            self.state = "MENU"

    def update(self):
        """
        Update game state (movement, collisions, score).
        """
        if self.state != "PLAYING" or self.paused:
            return

        # Update move timer
        self.move_timer += self.clock.get_time()

        # Only move snake when enough time has passed
        if self.move_timer >= self.move_delay:
            self.move_timer = 0

            # Move the snake (wrap optionally)
            if self.wrap_around:
                self.snake.move_wrap(PLAY_WIDTH, PLAY_HEIGHT, PLAY_LEFT, PLAY_TOP)
            else:
                self.snake.move()

            head = self.snake.get_head_position()

            # Check collision with obstacles
            if head in self.obstacles:
                self.state = "GAME_OVER"
                self.sound.play('gameover')
            
            # Check collision with food
            if head == self.food.get_position():
                self.snake.grow()
                self.score += 10
                self.sound.play('eat')
                # Spawn new food, avoiding snake body and obstacles
                avoid = list(self.snake.body) + list(self.obstacles)
                self.food.spawn(avoid_positions=avoid)
                # Maybe spawn a bonus food
                self.maybe_spawn_bonus()

            # Check collision with bonus food
            if self.bonus_pos and head == self.bonus_pos:
                self.snake.grow()
                self.score += BONUS_POINTS
                self.bonus_pos = None
                self.bonus_expire_at = 0
                self.sound.play('eat')

            # Expire bonus food if time passed
            if self.bonus_pos and pygame.time.get_ticks() >= self.bonus_expire_at:
                self.bonus_pos = None
                self.bonus_expire_at = 0

            # Check collisions with walls or self
            wall_hit = False if self.wrap_around else self.snake.check_collision_with_walls(
                PLAY_WIDTH, PLAY_HEIGHT, PLAY_LEFT, PLAY_TOP)
            if wall_hit or self.snake.check_collision_with_self():
                self.state = "GAME_OVER"
                self.sound.play('gameover')
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()

    def maybe_spawn_bonus(self):
        """Randomly spawn a temporary bonus food item."""
        if random.random() <= BONUS_CHANCE:
            # Find a spot avoiding snake and obstacles and regular food
            avoid = set(self.snake.body) | self.obstacles | {self.food.get_position()}
            grid_w = PLAY_WIDTH // GRID_SIZE
            grid_h = PLAY_HEIGHT // GRID_SIZE
            for _ in range(200):
                x = PLAY_LEFT + random.randint(0, grid_w - 1) * GRID_SIZE
                y = PLAY_TOP + random.randint(0, grid_h - 1) * GRID_SIZE
                if (x, y) not in avoid:
                    self.bonus_pos = (x, y)
                    self.bonus_expire_at = pygame.time.get_ticks() + BONUS_LIFETIME_MS
                    break

    def draw(self):
        """
        Draw all game elements based on current state.
        """
        # Draw everything onto the base-resolution surface
        surface = self.game_surface
        surface.fill(self.bg_color)

        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "SETTINGS":
            self.draw_settings()
        elif self.state == "PLAYING":
            self.draw_game()
        elif self.state == "GAME_OVER":
            self.draw_game()  # Show game in background
            self.draw_game_over()

        # Scale the rendered game to the actual window size, keeping the
        # aspect ratio (letterboxed with black bars when the window is not
        # exactly 4:3 -- e.g. while the user is still dragging a resize)
        win_w, win_h = self.screen.get_size()
        self.scale = min(win_w / WINDOW_WIDTH, win_h / WINDOW_HEIGHT)
        scaled_w = max(1, round(WINDOW_WIDTH * self.scale))
        scaled_h = max(1, round(WINDOW_HEIGHT * self.scale))
        self.offset = ((win_w - scaled_w) // 2, (win_h - scaled_h) // 2)

        self.screen.fill(BLACK)
        if (scaled_w, scaled_h) == self.base_size:
            self.screen.blit(surface, self.offset)
        else:
            scaled = pygame.transform.smoothscale(surface, (scaled_w, scaled_h))
            self.screen.blit(scaled, self.offset)

        # Update display
        pygame.display.flip()
    
    def draw_menu(self):
        """
        Draw the main menu.
        """
        # Title
        self.draw_text_centered("MAMBA GAME", WINDOW_HEIGHT // 2 - 150, CYAN, 72)
        
        # Buttons
        font = pygame.font.Font(None, 36)
        self.start_button.draw(self.game_surface, font)
        self.settings_button.draw(self.game_surface, font)
        self.quit_button.draw(self.game_surface, font)
        
        # High score
        if self.high_score > 0:
            self.draw_text_centered(f"High Score: {self.high_score}", WINDOW_HEIGHT - 50, YELLOW, 32)
    
    def draw_settings(self):
        """
        Draw the settings menu.
        """
        # Align layout
        self.layout_settings()
        # Title
        self.draw_text_centered("⚙️ SETTINGS", 80, CYAN, 64)
        self.draw_text_centered("Select Difficulty", 140, WHITE, 30)
        
        # Difficulty buttons
        font = pygame.font.Font(None, 32)
        for diff_name, button in self.difficulty_buttons.items():
            # Highlight selected difficulty
            if diff_name == self.difficulty:
                button.color = GREEN
                button.hover_color = DARK_GREEN
            else:
                button.color = DARK_GRAY
                button.hover_color = GRAY
            button.draw(self.game_surface, font)

        # Toggles & theme
        self.wrap_button.text = f"WRAP AROUND: {'ON' if self.wrap_around else 'OFF'}"
        self.obstacles_button.text = f"OBSTACLES: {'ON' if self.obstacles_enabled else 'OFF'}"
        self.theme_button.text = f"THEME: {self.theme_name}"
        self.wrap_button.draw(self.game_surface, font)
        self.obstacles_button.draw(self.game_surface, font)
        self.theme_button.draw(self.game_surface, font)

        # Back button
        self.back_button.draw(self.game_surface, font)
    
    def draw_game(self):
        """
        Draw the game (snake, food, score, input pad).
        """
        # Draw HUD/bottom bars and the play-area border first
        self.draw_bars()

        # Draw grid (optional visual enhancement)
        self.draw_grid()

        # Draw obstacles
        if self.obstacles:
            for (ox, oy) in self.obstacles:
                pygame.draw.rect(self.game_surface, DARK_GRAY, (ox, oy, GRID_SIZE, GRID_SIZE), border_radius=3)

        # Draw game objects
        if self.snake:
            self.snake.draw(self.game_surface)
        if self.food:
            self.food.draw(self.game_surface)

        # Draw bonus food if active (pulsing)
        if self.bonus_pos:
            bx, by = self.bonus_pos
            cx = bx + GRID_SIZE // 2
            cy = by + GRID_SIZE // 2
            base_radius = GRID_SIZE // 2 - 2
            pulse = 2 * ((pygame.time.get_ticks() // 100) % 2)  # small pulse
            pygame.draw.circle(self.game_surface, ORANGE, (cx, cy), base_radius - pulse)
            pygame.draw.circle(self.game_surface, WHITE, (cx, cy), max(2, (base_radius - 6)))

        # Draw HUD
        self.draw_hud()

        # Draw pause overlay if paused
        if self.paused:
            self.draw_pause()

        # Draw the input visualization on top so it stays visible (even when
        # paused) and never overlaps the play area
        self.draw_input_pad()

    def draw_bars(self):
        """
        Draw the HUD bar (top) and input bar (bottom) plus the play-area border,
        so text and widgets never overlap the game board.
        """
        surface = self.game_surface
        # Slightly lighter shade of the theme background for the bars
        bar_color = tuple(min(c + 18, 255) for c in self.bg_color)
        border_color = tuple(min(c + 60, 255) for c in self.bg_color)

        surface.fill(bar_color, (0, 0, WINDOW_WIDTH, HUD_BAR_HEIGHT))
        surface.fill(bar_color, (0, WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT,
                                 WINDOW_WIDTH, BOTTOM_BAR_HEIGHT))

        # Border around the play area
        pygame.draw.rect(surface, border_color,
                         (PLAY_LEFT, PLAY_TOP, PLAY_WIDTH, PLAY_HEIGHT), 2)

    def draw_input_pad(self):
        """
        Draw the D-pad style input visualization in the bottom bar.

        Four arrow tiles are laid out in a plus shape; a tile lights up
        (bright fill + glow) for INPUT_FLASH_MS whenever the matching
        direction comes in via keyboard or voice.
        """
        now = pygame.time.get_ticks()
        ts, gap = INPUT_PAD_TILE, INPUT_PAD_GAP
        # Center the plus-shaped pad in the bottom bar
        pad_cx = WINDOW_WIDTH // 2
        y0 = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT + (BOTTOM_BAR_HEIGHT - (2 * ts + gap)) // 2

        tiles = {
            UP:    (pad_cx - ts // 2, y0),
            LEFT:  (pad_cx - ts // 2 - ts - gap, y0 + ts + gap),
            DOWN:  (pad_cx - ts // 2, y0 + ts + gap),
            RIGHT: (pad_cx + ts // 2 + gap, y0 + ts + gap),
        }

        surface = self.game_surface
        for direction, (tx, ty) in tiles.items():
            active = (now - self.input_flash.get(direction, -10 ** 9)) < INPUT_FLASH_MS
            rect = pygame.Rect(tx, ty, ts, ts)

            if active:
                # Glow ring around the lit tile
                glow = rect.inflate(6, 6)
                pygame.draw.rect(surface, AMBER, glow, width=2, border_radius=7)
                pygame.draw.rect(surface, AMBER, rect, border_radius=5)
                pygame.draw.rect(surface, WHITE, rect, width=1, border_radius=5)
                arrow_color = (40, 40, 40)
            else:
                pygame.draw.rect(surface, (45, 45, 45), rect, border_radius=7)
                pygame.draw.rect(surface, (90, 90, 90), rect, width=1, border_radius=7)
                arrow_color = (150, 150, 150)

            # Arrow polygon inside the tile
            m = 5  # margin
            cx, cy = rect.center
            if direction == UP:
                points = [(cx, ty + m), (tx + m, ty + ts - m), (tx + ts - m, ty + ts - m)]
            elif direction == DOWN:
                points = [(cx, ty + ts - m), (tx + m, ty + m), (tx + ts - m, ty + m)]
            elif direction == LEFT:
                points = [(tx + m, cy), (tx + ts - m, ty + m), (tx + ts - m, ty + ts - m)]
            else:  # RIGHT
                points = [(tx + ts - m, cy), (tx + m, ty + m), (tx + m, ty + ts - m)]
            pygame.draw.polygon(surface, arrow_color, points)

        # Show the last received input word on the left of the pad
        if self.last_input_word:
            recent = (now - self.last_input_time) < INPUT_FLASH_MS
            color = AMBER if recent else GRAY
            self.draw_text(f'Heard: "{self.last_input_word}"', 24,
                           WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT + 20, color, 22)

        # Controls hint on the right of the pad
        self.draw_text("P: Pause | ESC: Menu", WINDOW_WIDTH - 220,
                       WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT + 22, GRAY, 20)
    
    def draw_grid(self):
        """
        Draw a subtle grid for visual reference.
        Lines are drawn inside the play area only, aligned to its origin so
        they line up with the snake/food cells.
        """
        grid_color = self.grid_color
        for x in range(PLAY_LEFT, PLAY_LEFT + PLAY_WIDTH + 1, GRID_SIZE):
            pygame.draw.line(self.game_surface, grid_color,
                             (x, PLAY_TOP), (x, PLAY_TOP + PLAY_HEIGHT))
        for y in range(PLAY_TOP, PLAY_TOP + PLAY_HEIGHT + 1, GRID_SIZE):
            pygame.draw.line(self.game_surface, grid_color,
                             (PLAY_LEFT, y), (PLAY_LEFT + PLAY_WIDTH, y))
    
    def draw_hud(self):
        """
        Draw the heads-up display in the top bar (above the play area).
        """
        # Score
        self.draw_text(f"Score: {self.score}", 20, 6, WHITE, 32)

        # High score
        if self.high_score > 0:
            self.draw_text(f"Best: {self.high_score}", 20, 36, YELLOW, 22)

        # Difficulty indicator
        self.draw_text(f"Difficulty: {self.difficulty}", WINDOW_WIDTH - 360, 6, CYAN, 22)

        # Snake length
        if self.snake:
            self.draw_text(f"Length: {self.snake.get_length()}", WINDOW_WIDTH - 360, 34, GREEN, 22)

        # Voice command status
        if self.voice_client.connected:
            self.draw_text("Voice: ON", WINDOW_WIDTH - 130, 20, GREEN, 22)
        else:
            self.draw_text("Voice: OFF", WINDOW_WIDTH - 130, 20, GRAY, 22)

    def draw_text(self, text, x, y, color, size=24):
        """
        Draw text on the screen at specific position.
        
        Args:
            text (str): Text to display
            x (int): X-coordinate
            y (int): Y-coordinate
            color (tuple): RGB color tuple
            size (int): Font size
        """
        try:
            font = pygame.font.Font(None, size)
            text_surface = font.render(text, True, color)
            self.game_surface.blit(text_surface, (x, y))
        except Exception as e:
            print(f"Error drawing text: {e}")
    
    def draw_text_centered(self, text, y, color, size=24):
        """
        Draw centered text on the screen.
        
        Args:
            text (str): Text to display
            y (int): Y-coordinate
            color (tuple): RGB color tuple
            size (int): Font size
        """
        try:
            font = pygame.font.Font(None, size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.game_surface.blit(text_surface, text_rect)
        except Exception as e:
            print(f"Error drawing text: {e}")

    def draw_game_over(self):
        """
        Draw the game over screen with score and options.
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.game_surface.blit(overlay, (0, 0))
        
        # Game over text with shadow effect
        self.draw_text_centered("GAME OVER!", WINDOW_HEIGHT // 2 - 102, BLACK, 68)
        self.draw_text_centered("GAME OVER!", WINDOW_HEIGHT // 2 - 100, RED, 68)
        
        # Score display
        self.draw_text_centered(f"Final Score: {self.score}", WINDOW_HEIGHT // 2 - 10, WHITE, 42)
        
        # High score
        if self.score >= self.high_score:
            self.draw_text_centered("🏆 NEW HIGH SCORE! 🏆", WINDOW_HEIGHT // 2 + 40, YELLOW, 36)
        elif self.high_score > 0:
            self.draw_text_centered(f"High Score: {self.high_score}", WINDOW_HEIGHT // 2 + 40, YELLOW, 32)
        
        # Buttons
        font = pygame.font.Font(None, 36)
        self.restart_button.draw(self.game_surface, font)
        self.menu_button.draw(self.game_surface, font)
        
        # Hint
        self.draw_text_centered("Press SPACE to restart or ESC for menu", WINDOW_HEIGHT - 50, LIGHT_GRAY, 24)

    def draw_pause(self):
        """
        Draw the pause screen overlay.
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.game_surface.blit(overlay, (0, 0))
        
        # Pause text with shadow
        self.draw_text_centered("⏸️ PAUSED", WINDOW_HEIGHT // 2 - 52, BLACK, 68)
        self.draw_text_centered("⏸️ PAUSED", WINDOW_HEIGHT // 2 - 50, YELLOW, 68)
        
        # Instructions
        self.draw_text_centered("Press P to continue", WINDOW_HEIGHT // 2 + 30, WHITE, 32)
        self.draw_text_centered("Press ESC for menu", WINDOW_HEIGHT // 2 + 70, LIGHT_GRAY, 28)

    def run(self):
        """
        Main game loop.
        """
        running = True
        
        try:
            while running:
                # Handle events
                running = self.handle_events()
                
                # Handle voice commands from the word socket
                self.handle_word_commands()
                
                # Update game state
                self.update()
                
                # Draw everything
                self.draw()
                
                # Control frame rate
                self.clock.tick(FPS)
        
        except Exception as e:
            print(f"Error in game loop: {e}")
        
        finally:
            self.voice_client.stop()
            pygame.quit()
            sys.exit()


def main():
    """
    Entry point for the game.
    """
    print("=" * 60)
    print("Python Mamba Game")
    print("=" * 60)
    print("Controls:")
    print("  ↑ ↓ ← → : Move snake")
    print("  P       : Pause/Resume")
    print("  ESC     : Menu/Quit")
    print("  Voice   : Say left/right/up/down, go, stop (KWS word socket)")
    print("=" * 60)
    print("\nStarting game...\n")
    
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Goodbye!")
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
    finally:
        # Best-effort cleanup of the socket thread if still running
        try:
            if 'game' in locals() and game is not None:
                game.voice_client.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
