# Python Snake Game 🐍

A fully functional classic Snake Game built with Python 3.14 and Pygame.

![Snake Game](https://via.placeholder.com/800x600.png?text=Snake+Game+Screenshot)

## 🎮 Features

- **Main Menu System**: Professional menu interface with button interactions
- **Settings Menu**: Customize difficulty, toggle wrap-around, obstacles, and themes
- **Themes**: Classic, Neon, Matrix (applies background, snake, food, grid colors)
- **Adjustable Speed**: Choose from 5 to 20 moves per second based on difficulty
- **Classic Snake Gameplay**: Navigate the snake to eat food and grow longer
- **Bonus Food**: Rare timed item worth +50 points with pulsing effect
- **Obstacles (optional)**: Random blocks added for an extra challenge
- **Wrap-around Mode (optional)**: Go through walls and appear on the opposite side
- **Score Tracking**: Real-time score with persistent high score saved locally
- **Voice Control**: Control the snake via the KWS word socket (speak left/right/up/down)
- **Smooth Movement**: Time-based movement system (not frame-dependent)
- **Pause Functionality**: Pause and resume gameplay at any time
- **Enhanced UI**: Modern design with hover effects, shadows, and grid overlay
- **Game Over Screen**: Detailed stats with restart and menu options
- **Optional Sounds**: Add eat.wav, gameover.wav, click.wav to enable effects
- **Clean Code**: Modular OOP design with comprehensive documentation

## 🛠️ Requirements

- **Python 3.14** or higher
- **Pygame** (latest version)

## 📦 Installation

### Step 1: Clone or Download the Repository

```bash
cd "d:\Python Snake Game"
```

### Step 2: Install Dependencies

```bash
pip install pygame
```

Or if you have multiple Python versions:

```bash
python -m pip install pygame
```

## 🚀 How to Run

### Windows (PowerShell/CMD)

```bash
python main.py
```

Or use the full path:

```bash
C:/Users/LENOVO/AppData/Local/Programs/Python/Python314/python.exe main.py
```

### The game window should open automatically!

## 🎯 How to Play

### Main Menu

- **START GAME**: Begin playing immediately with current settings
- **SETTINGS**: Adjust difficulty level
- **QUIT**: Exit the game

### Difficulty Levels

| Level | Speed | Description |
|-------|-------|-------------|
| Easy | 5 moves/sec | Perfect for beginners |
| Medium | 10 moves/sec | Balanced challenge |
| Hard | 15 moves/sec | For experienced players |
| Extreme | 20 moves/sec | Ultimate challenge! |

### Controls

| Key | Action |
|-----|--------|
| ↑ (Up Arrow) | Move Up |
| ↓ (Down Arrow) | Move Down |
| ← (Left Arrow) | Move Left |
| → (Right Arrow) | Move Right |
| P | Pause/Resume |
| ESC | Return to Menu / Quit |
| SPACE | Restart (when game over) |
| Mouse Click | Menu interactions |
| Voice | Say left/right/up/down to move, go to start, stop to pause |

### Game Over

- Your score is displayed along with the high score
- Click **RESTART** or press **SPACE** to play again
- Click **MAIN MENU** or press **ESC** to return to menu

### Objective

1. Control the snake using arrow keys
2. Eat the red food to grow longer
3. Avoid hitting the walls
4. Avoid hitting your own body
5. Try to get the highest score possible!
6. Challenge yourself with higher difficulty levels!

## 🎤 Voice Control (KWS Word Socket)

The game connects to the KWS word socket (see `socket_docs.md`) which pushes
the keywords guessed by the speech model as plain-text lines. It reconnects
automatically, so start it before or after the demo server — the game will
pick it up within a couple of seconds. Connection status (Voice: ON/OFF) is
shown in the in-game HUD.

| Spoken word | Effect |
|-------------|--------|
| left / right / up / down | Turn the snake (same as arrow keys) |
| go | Start the game, resume from pause, or restart after game over |
| stop | Pause the game |
| other words (yes, no, off, on, silence, unknown) | Ignored |

## 📁 Project Structure

```
d:\Python Snake Game\
│
├── main.py          # Main game loop and Game class
├── snake.py         # Snake class with movement and collision logic
├── food.py          # Food class with spawning logic
├── config.py        # Game configuration and constants
├── word_socket.py   # KWS word socket client (voice commands)
├── test_snake.py    # Unit tests for game logic
├── README.md        # This file
└── Master-prompt.md # Original project prompt
```

## 🧪 Running Tests

The project includes comprehensive unit tests for snake movement, growth, and collision detection.

### Run all tests:

```bash
python test_snake.py
```

### Using unittest directly:

```bash
python -m unittest test_snake -v
```

### Expected Output:

```
Running Snake Game Unit Tests
====================================
test_initial_position ... ok
test_movement_right ... ok
test_growth ... ok
test_collision_with_self ... ok
...
------------------------------------
Ran XX tests in X.XXXs

OK
```

## ⚙️ Configuration

You can customize the game by editing `config.py`:

```python
# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Difficulty levels (moves per second)
DIFFICULTY_LEVELS = {
    'Easy': 5,      # 5 moves per second
    'Medium': 10,   # 10 moves per second
    'Hard': 15,     # 15 moves per second
    'Extreme': 20   # 20 moves per second
}

# Grid size (affects snake and food size)
GRID_SIZE = 20

# Colors (R, G, B)
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (213, 50, 80)
BG_COLOR = (0, 0, 0)
```

### Optional toggles and extras

- Enable wrap-around or obstacles from the in-game Settings menu
- Themes can be switched live: Classic, Neon, Matrix
- Bonus food spawns randomly and lasts ~5 seconds
- Sounds are optional: drop `eat.wav`, `gameover.wav`, `click.wav` in the project root

## 🐛 Troubleshooting

### "pygame not found" error

Install pygame:
```bash
pip install pygame
```

### "Python not recognized" error

Use the full path to Python:
```bash
C:/Users/LENOVO/AppData/Local/Programs/Python/Python314/python.exe main.py
```

### Game runs too fast or too slow

- Go to **SETTINGS** in the main menu
- Choose a different difficulty level
- Easy (5 moves/sec) is recommended for beginners

### Can't control the snake properly

- Make sure the game window has focus
- The snake cannot reverse direction (can't turn 180°)
- Try starting with Easy difficulty to get comfortable

### Import errors

Make sure all files are in the same directory and you're running from the project root.

## 🎨 Game Mechanics

- **Starting Length**: 3 segments
- **Growth**: +1 segment per food eaten
- **Score**: +10 points per food eaten
- **Speed Control**: Time-based movement (not frame-dependent)
- **Difficulty Levels**: 4 levels with different speeds
- **Grid-based Movement**: Smooth, predictable movement on a grid
- **High Score Tracking**: Your best score is saved during the session
- **Menu System**: Intuitive mouse and keyboard navigation

## 🧩 Code Quality

- **PEP 8 Compliant**: Follows Python style guidelines
- **Modular Design**: Separate classes for Snake, Food, and Game
- **Comprehensive Comments**: Docstrings for all classes and methods
- **Exception Handling**: Graceful error handling throughout
- **Unit Tested**: Comprehensive test coverage

## 📝 Credits

Built by YOU.

- Development Date: October 25, 2025
- Python Version: 3.14
- Framework: Pygame

## 📄 License

This project is open source and available for educational purposes.

## 🎉 Enjoy the Game!

Have fun playing the classic Snake Game! Try to beat your high score! 🐍🎮

---

**Need help?** Check the troubleshooting section or review the code comments for detailed explanations.
