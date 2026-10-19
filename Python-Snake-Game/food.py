"""
Food class implementation
Handles food spawning and rendering
"""

import pygame
import random
from config import *


class Food:
    """
    Food class representing the food items the snake eats.
    """

    def __init__(self, window_width, window_height, offset=(0, 0)):
        """
        Initialize food at a random position.
        
        Args:
            window_width (int): Play area width
            window_height (int): Play area height
            offset (tuple, optional): (x, y) origin of the play area on screen
        """
        self.window_width = window_width
        self.window_height = window_height
        self.offset_x, self.offset_y = offset
        self.position = self.spawn()
        self.color = FOOD_COLOR

    def set_color(self, color):
        """Set food color at runtime (for themes)."""
        self.color = color

    def spawn(self, avoid_positions=None):
        """
        Spawn food at a random grid-aligned position.
        
        Args:
            avoid_positions (list, optional): List of positions to avoid
        
        Returns:
            tuple: (x, y) coordinates of the food
        """
        if avoid_positions is None:
            avoid_positions = []
        
        # Calculate number of grid cells
        grid_width = self.window_width // GRID_SIZE
        grid_height = self.window_height // GRID_SIZE
        
        # Generate random position until we find one not in avoid_positions
        while True:
            x = self.offset_x + random.randint(0, grid_width - 1) * GRID_SIZE
            y = self.offset_y + random.randint(0, grid_height - 1) * GRID_SIZE
            position = (x, y)
            
            if position not in avoid_positions:
                self.position = position
                return position

    def get_position(self):
        """
        Get the current position of the food.
        
        Returns:
            tuple: (x, y) coordinates of the food
        """
        return self.position

    def draw(self, surface):
        """
        Draw the food on the given pygame surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        x, y = self.position
        
        # Draw food as a filled circle
        center_x = x + GRID_SIZE // 2
        center_y = y + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 2

        pygame.draw.circle(surface, self.color, (center_x, center_y), radius)
        
        # Add a small highlight for visual effect
        highlight_offset = radius // 3
        pygame.draw.circle(surface, WHITE, 
                         (center_x - highlight_offset, center_y - highlight_offset), 
                         radius // 4)
