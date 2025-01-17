import pygame
import sys
from game_engine import *
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
"""
main.py

This module is the entry point for the King's Trial game.
It initializes the game engine, sets up the main loop, and handles user input.

Features:
- Game initialization and setup.
- Main loop for event handling, state updates, and rendering.
- Integration with the Game class for managing game logic.
"""
pygame.init()
        
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()