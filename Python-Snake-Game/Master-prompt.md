Title: Build, Test, and Debug a Complete Snake Game in Python 3.14
🎯 GOAL

You are GitHub Copilot Agent running in VS Code on Windows 11.
Your objective is to build a fully functional classic Snake Game using Python 3.14 (latest) with the following goals:

Complete in one execution — create, test, and run the game successfully.

Self-debug and self-correct until no runtime or syntax errors remain.

Organize the project into clean, maintainable code with comments and modular design.

Ensure the final game runs smoothly in a resizable window using pygame (latest version).

Include testing scripts for logic and movement.

Provide clear run instructions for Windows 11 + Python 3.14.

🏗️ PROJECT REQUIREMENTS
1. Environment Setup

Use Python 3.14 interpreter.

Ensure dependencies:

pip install pygame


Automatically verify dependencies; if missing, prompt installation or handle gracefully.

2. Project Structure
snake_game/
│
├── main.py
├── snake.py
├── food.py
├── config.py
├── test_snake.py
└── README.md

3. Functionality Requirements

Implement classic Snake gameplay:

Arrow-key control

Growing snake length after eating food

Increasing difficulty or speed as score increases

Game-over condition when snake hits walls or itself

Display:

Real-time score counter

Restart option after game-over

Window title: "Python Snake Game 🐍 - Powered by Copilot AI"

Frame rate: 10–20 FPS adjustable in config.py.

4. Code Quality

Use PEP 8 style guide.

Add inline comments and docstrings for every class and function.

Use modular OOP structure — Snake, Food, and Game classes.

Handle all exceptions gracefully with descriptive messages.

🧩 TESTING REQUIREMENTS

Write a test_snake.py using unittest:

Test snake movement logic (no out-of-bound errors)

Test growth when eating food

Test collision detection

Ensure all tests pass before final run.

🧠 EXECUTION FLOW

Copilot Agent should:

Create all necessary files.

Write full code for each module (snake.py, food.py, config.py, main.py).

Write test_snake.py and run pytest or unittest.

Debug and re-run if errors occur — automatically refactor broken logic.

Finally, run the game with:

python main.py


Confirm game window launches and runs properly.

🧪 DEBUGGING LOGIC

If any runtime error or failed test occurs:

Automatically identify traceback source.

Suggest and apply the fix.

Re-run the failed component until all tests pass.

📦 DOCUMENTATION

Generate a README.md with:

Installation steps

Run instructions

Keybindings

Screenshot placeholder (use Markdown image link)

Credits: “Built by GitHub Copilot Agent (prompted by ChatGPT)”

✅ COMPLETION CRITERIA

Copilot Agent should report success only when:

Game runs interactively with no errors.

All tests in test_snake.py pass.

Code is formatted and documented.

README.md is generated.

🚀 BONUS (Optional Enhancements)

Add start menu and pause functionality.

Save high score locally (highscore.txt).

Add simple background music using pygame.mixer.

🧭 FINAL COMMAND

Execute the following sequence automatically:
# Install dependencies
# Write tests and run them
pytest --maxfail=1 --disable-warnings -q
python main.py

💬 END PROMPT MESSAGE

You are a self-correcting Copilot Agent.
Continue iterating and debugging until the Snake Game runs perfectly without manual intervention.
Confirm completion with:
"✅ All tests passed. Game running successfully on Python 3.14."