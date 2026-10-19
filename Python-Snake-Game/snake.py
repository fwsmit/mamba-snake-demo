"""
Snake class implementation
Handles snake movement, growth, and collision detection
"""

import pygame
from config import *


class Snake:
    # Runtime-adjustable colors (can be themed via Game)
    body_color = SNAKE_COLOR
    head_color = SNAKE_HEAD_COLOR

    @classmethod
    def set_colors(cls, body_color, head_color):
        """Set snake colors at runtime (for themes)."""
        cls.body_color = body_color
        cls.head_color = head_color
    """
    Snake class representing the player-controlled snake.
    """

    def __init__(self, x, y):
        """
        Initialize the snake at given position.
        
        Args:
            x (int): Initial x-coordinate
            y (int): Initial y-coordinate
        """
        self.body = [(x, y), (x - GRID_SIZE, y), (x - 2 * GRID_SIZE, y)]
        self.direction = RIGHT
        self.grow_pending = False

    def move(self):
        """
        Move the snake in the current direction.
        If grow_pending is True, the snake grows by one segment.
        """
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        
        # Calculate new head position
        new_head = (head_x + dir_x * GRID_SIZE, head_y + dir_y * GRID_SIZE)
        
        # Add new head to the front
        self.body.insert(0, new_head)
        
        # Remove tail if not growing
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

    def move_wrap(self, width, height, offset_x=0, offset_y=0):
        """
        Move the snake with wrap-around at the edges of a play area.

        Args:
            width (int): Play area width
            height (int): Play area height
            offset_x (int, optional): X-coordinate of the play area's left edge
            offset_y (int, optional): Y-coordinate of the play area's top edge
        """
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x * GRID_SIZE, head_y + dir_y * GRID_SIZE)

        # Wrap using modulo on grid (relative to the play area origin)
        wrapped_x = offset_x + (new_head[0] - offset_x) % width
        wrapped_y = offset_y + (new_head[1] - offset_y) % height
        self.body.insert(0, (wrapped_x, wrapped_y))

        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

    def change_direction(self, new_direction):
        """
        Change the snake's direction if it's not opposite to current direction.
        
        Args:
            new_direction (tuple): New direction tuple (dx, dy)
        """
        # Prevent 180-degree turns
        current_dir_x, current_dir_y = self.direction
        new_dir_x, new_dir_y = new_direction
        
        if (current_dir_x + new_dir_x != 0) or (current_dir_y + new_dir_y != 0):
            self.direction = new_direction

    def grow(self):
        """
        Mark the snake to grow on the next move.
        """
        self.grow_pending = True

    def check_collision_with_self(self):
        """
        Check if the snake's head collides with its body.
        
        Returns:
            bool: True if collision detected, False otherwise
        """
        head = self.body[0]
        return head in self.body[1:]

    def check_collision_with_walls(self, width, height, offset_x=0, offset_y=0):
        """
        Check if the snake's head collides with the play area boundaries.
        
        Args:
            width (int): Play area width
            height (int): Play area height
            offset_x (int, optional): X-coordinate of the play area's left edge
            offset_y (int, optional): Y-coordinate of the play area's top edge
        
        Returns:
            bool: True if collision detected, False otherwise
        """
        head_x, head_y = self.body[0]
        rel_x = head_x - offset_x
        rel_y = head_y - offset_y
        
        return (rel_x < 0 or rel_x >= width or 
                rel_y < 0 or rel_y >= height)

    def get_head_position(self):
        """
        Get the current position of the snake's head.
        
        Returns:
            tuple: (x, y) coordinates of the head
        """
        return self.body[0]

    def draw(self, surface):
        """
        Draw the snake on the given pygame surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        for i, segment in enumerate(self.body):
            x, y = segment
            
            # Draw head with different color
            if i == 0:
                color = Snake.head_color
            else:
                color = Snake.body_color
            
            pygame.draw.rect(surface, color, (x, y, GRID_SIZE, GRID_SIZE))
            
            # Add a border to make segments distinct
            pygame.draw.rect(surface, BG_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)

    def get_length(self):
        """
        Get the current length of the snake.
        
        Returns:
            int: Number of segments in the snake
        """
        return len(self.body)
