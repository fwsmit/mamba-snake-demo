"""
Configuration file for Snake Game
Contains all game settings and constants
"""

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Python Snake Game 🐍"

# Screen layout: a HUD bar on top and an input-visualizer bar at the bottom,
# with the play area (grid) sandwiched in between. This keeps HUD text from
# ever overlapping the game board.
HUD_BAR_HEIGHT = 60                          # Top bar: score/best/difficulty/voice status
BOTTOM_BAR_HEIGHT = 60                       # Bottom bar: input pad + hints
PLAY_WIDTH = WINDOW_WIDTH                    # Play area size (must stay grid-aligned)
PLAY_HEIGHT = WINDOW_HEIGHT - HUD_BAR_HEIGHT - BOTTOM_BAR_HEIGHT  # 800x480 = 20x12 cells
PLAY_LEFT = 0
PLAY_TOP = HUD_BAR_HEIGHT
PLAY_OFFSET = (PLAY_LEFT, PLAY_TOP)          # Where the play area sits on screen

# Input visualization (arrow pad in the bottom bar)
INPUT_PAD_TILE = 24                          # Size of one arrow tile in px
INPUT_PAD_GAP = 3                            # Gap between arrow tiles in px
INPUT_FLASH_MS = 300                         # How long an arrow stays lit after input

# Game settings
GRID_SIZE = 40  # Size of each grid cell in pixels
FPS = 60  # Frame rate for smooth rendering (rendering only; movement is time-based)
INITIAL_SPEED = FPS
SPEED_INCREMENT = 0  # Increase speed as score grows (0 = constant speed)

# Difficulty settings (moves per second)
DIFFICULTY_LEVELS = {
    'Easy': 1,
    'Medium': 2,
    'Hard': 4,
    'Extreme': 6
}
DEFAULT_DIFFICULTY = 'Medium'

# Gameplay toggles
WRAP_AROUND_DEFAULT = False  # If True, snake wraps around edges instead of dying
OBSTACLES_DEFAULT = False    # If True, random obstacles appear in the arena
OBSTACLE_COUNT = 20          # Number of obstacle blocks when enabled

# Bonus food settings
BONUS_CHANCE = 0.2           # 20% chance to spawn bonus food after eating
BONUS_POINTS = 50            # Points for bonus food
BONUS_LIFETIME_MS = 10000     # Bonus food lifetime in milliseconds

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
DARK_GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
AMBER = (255, 210, 0)

# Snake colors
SNAKE_COLOR = GREEN
SNAKE_HEAD_COLOR = DARK_GREEN

# Food color
FOOD_COLOR = RED

# Background color
BG_COLOR = BLACK

# Text color
TEXT_COLOR = WHITE

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Themes (can be selected in settings)
THEMES = {
    'Classic': {
        'bg': BLACK,
        'snake': GREEN,
        'snake_head': DARK_GREEN,
        'food': RED,
        'grid': (20, 20, 20),
    },
    'Neon': {
        'bg': (10, 10, 20),
        'snake': (0, 255, 170),
        'snake_head': (255, 0, 200),
        'food': (255, 255, 0),
        'grid': (30, 30, 50),
    },
    'Matrix': {
        'bg': (5, 15, 5),
        'snake': (0, 200, 70),
        'snake_head': (0, 255, 110),
        'food': (140, 255, 140),
        'grid': (15, 30, 15),
    },
}
DEFAULT_THEME = 'Classic'

# High score persistence
HIGHSCORE_FILE = 'highscore.txt'

# KWS word socket (see socket_docs.md)
SOCKET_HOST = "127.0.0.1"    # Voice command server host
SOCKET_PORT = 8765           # Voice command server port
SOCKET_RECONNECT_DELAY = 2.0 # Seconds between connection attempts
