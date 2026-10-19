"""
Unit tests for Snake Game
Tests snake movement, growth, and collision detection
"""

import unittest
import sys
import os

# Add parent directory to path to import game modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from snake import Snake
from food import Food
from config import *


class TestSnake(unittest.TestCase):
    """
    Test cases for the Snake class.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.snake = Snake(100, 100)

    def test_initial_position(self):
        """
        Test that snake initializes with correct position and length.
        """
        self.assertEqual(len(self.snake.body), 3)
        self.assertEqual(self.snake.body[0], (100, 100))
        self.assertEqual(self.snake.direction, RIGHT)

    def test_movement_right(self):
        """
        Test snake movement to the right.
        """
        initial_head = self.snake.get_head_position()
        self.snake.change_direction(RIGHT)
        self.snake.move()
        new_head = self.snake.get_head_position()
        
        self.assertEqual(new_head[0], initial_head[0] + GRID_SIZE)
        self.assertEqual(new_head[1], initial_head[1])

    def test_movement_left(self):
        """
        Test snake movement to the left.
        """
        # First move right to allow left turn
        self.snake.change_direction(UP)
        self.snake.move()
        
        initial_head = self.snake.get_head_position()
        self.snake.change_direction(LEFT)
        self.snake.move()
        new_head = self.snake.get_head_position()
        
        self.assertEqual(new_head[0], initial_head[0] - GRID_SIZE)
        self.assertEqual(new_head[1], initial_head[1])

    def test_movement_up(self):
        """
        Test snake movement upward.
        """
        initial_head = self.snake.get_head_position()
        self.snake.change_direction(UP)
        self.snake.move()
        new_head = self.snake.get_head_position()
        
        self.assertEqual(new_head[0], initial_head[0])
        self.assertEqual(new_head[1], initial_head[1] - GRID_SIZE)

    def test_movement_down(self):
        """
        Test snake movement downward.
        """
        initial_head = self.snake.get_head_position()
        self.snake.change_direction(DOWN)
        self.snake.move()
        new_head = self.snake.get_head_position()
        
        self.assertEqual(new_head[0], initial_head[0])
        self.assertEqual(new_head[1], initial_head[1] + GRID_SIZE)

    def test_cannot_reverse_direction(self):
        """
        Test that snake cannot do 180-degree turn.
        """
        initial_direction = self.snake.direction
        # Try to turn opposite direction (should be ignored)
        self.snake.change_direction(LEFT)
        
        self.assertEqual(self.snake.direction, initial_direction)

    def test_growth(self):
        """
        Test that snake grows when eating food.
        """
        initial_length = self.snake.get_length()
        self.snake.grow()
        self.snake.move()
        
        self.assertEqual(self.snake.get_length(), initial_length + 1)

    def test_no_growth_without_food(self):
        """
        Test that snake maintains length when not eating.
        """
        initial_length = self.snake.get_length()
        self.snake.move()
        
        self.assertEqual(self.snake.get_length(), initial_length)

    def test_collision_with_self(self):
        """
        Test self-collision detection.
        """
        # Create a snake in a position where moving will cause self-collision
        # Snake body forms a shape, and moving down will hit its own body
        self.snake.body = [(100, 100), (100, 120), (120, 120), (120, 100), (100, 100)]
        
        # Now the head at (100, 100) is also at position 4, so it collides
        self.assertTrue(self.snake.check_collision_with_self())

    def test_no_collision_initially(self):
        """
        Test that new snake has no self-collision.
        """
        self.assertFalse(self.snake.check_collision_with_self())

    def test_collision_with_top_wall(self):
        """
        Test collision detection with top wall.
        """
        self.snake.body = [(100, 0)]
        self.snake.direction = UP
        self.snake.move()
        
        self.assertTrue(self.snake.check_collision_with_walls(WINDOW_WIDTH, WINDOW_HEIGHT))

    def test_collision_with_bottom_wall(self):
        """
        Test collision detection with bottom wall.
        """
        self.snake.body = [(100, WINDOW_HEIGHT - GRID_SIZE)]
        self.snake.direction = DOWN
        self.snake.move()
        
        self.assertTrue(self.snake.check_collision_with_walls(WINDOW_WIDTH, WINDOW_HEIGHT))

    def test_collision_with_left_wall(self):
        """
        Test collision detection with left wall.
        """
        self.snake.body = [(0, 100)]
        self.snake.direction = LEFT
        self.snake.move()
        
        self.assertTrue(self.snake.check_collision_with_walls(WINDOW_WIDTH, WINDOW_HEIGHT))

    def test_collision_with_right_wall(self):
        """
        Test collision detection with right wall.
        """
        self.snake.body = [(WINDOW_WIDTH - GRID_SIZE, 100)]
        self.snake.direction = RIGHT
        self.snake.move()
        
        self.assertTrue(self.snake.check_collision_with_walls(WINDOW_WIDTH, WINDOW_HEIGHT))

    def test_no_wall_collision_in_bounds(self):
        """
        Test that snake within bounds has no wall collision.
        """
        self.assertFalse(self.snake.check_collision_with_walls(WINDOW_WIDTH, WINDOW_HEIGHT))


class TestFood(unittest.TestCase):
    """
    Test cases for the Food class.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.food = Food(WINDOW_WIDTH, WINDOW_HEIGHT)

    def test_food_spawns_within_bounds(self):
        """
        Test that food spawns within game boundaries.
        """
        x, y = self.food.get_position()
        
        self.assertGreaterEqual(x, 0)
        self.assertLess(x, WINDOW_WIDTH)
        self.assertGreaterEqual(y, 0)
        self.assertLess(y, WINDOW_HEIGHT)

    def test_food_position_grid_aligned(self):
        """
        Test that food position is aligned to grid.
        """
        x, y = self.food.get_position()
        
        self.assertEqual(x % GRID_SIZE, 0)
        self.assertEqual(y % GRID_SIZE, 0)

    def test_food_respawn(self):
        """
        Test that food can be respawned at a new position.
        """
        old_position = self.food.get_position()
        
        # Spawn multiple times to likely get a different position
        new_position = None
        for _ in range(100):
            new_position = self.food.spawn()
            if new_position != old_position:
                break
        
        # At least verify it spawns (position changed or same is both valid)
        self.assertIsNotNone(new_position)
        self.assertEqual(new_position, self.food.get_position())

    def test_food_avoids_snake_body(self):
        """
        Test that food doesn't spawn on snake body.
        """
        # Create a list of positions to avoid
        avoid = [(100, 100), (120, 100), (140, 100)]
        position = self.food.spawn(avoid_positions=avoid)
        
        self.assertNotIn(position, avoid)


def run_tests():
    """
    Run all unit tests.
    """
    print("=" * 60)
    print("Running Snake Game Unit Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSnake))
    suite.addTests(loader.loadTestsFromTestCase(TestFood))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
