import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
"""
levels.py

This module defines the level design and configurations for the Jump King Recreation game.
It provides platform data and level backgrounds for rendering.

Features:
- Predefined platform layouts for each level.
- Background images for different levels.
- Utility functions for extracting platform data from images.
"""
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def extract_platforms(image_path):
    """
    Extract platform positions from an image file based on non-transparent pixels.

    Args:
        image_path (str): Path to the image file containing the platform layout.

    Returns:
        list[pygame.Rect]: A list of pygame.Rect objects representing platform positions and sizes.
    """
    platform_image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    platform_mask = pygame.mask.from_surface(platform_image)
    platforms = []

    for y in range(platform_mask.get_size()[1]):
        for x in range(platform_mask.get_size()[0]):
            if platform_mask.get_at((x, y)):
                rect = pygame.Rect(x, y, 1, 1)

                while rect.right < platform_mask.get_size()[0] and platform_mask.get_at((rect.right, rect.y)):
                    rect.width += 1
                while rect.bottom < platform_mask.get_size()[1] and platform_mask.get_at((rect.x, rect.bottom)):
                    rect.height += 1

                platforms.append(rect)

                for px in range(rect.x, rect.right):
                    for py in range(rect.y, rect.bottom):
                        platform_mask.set_at((px, py), 0)
    return platforms

LEVEL_BACKGROUNDS = [
    pygame.transform.scale(pygame.image.load(f"assets/background/mapa{i + 1}.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)) for i in range(22)
]

LEVEL_PLATFORMS = [
    extract_platforms(f"assets/platforms/mapa{i + 1}sama.png") for i in range(22)
]


