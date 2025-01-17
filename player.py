import pygame
import time
import os
from constants import *
from game_engine import *
from levels import *
"""
player.py

This module defines the Player class, which manages player behavior and interactions within the game.
It handles movement, jumping mechanics, collision detection, and animations.

Features:
- Player movement and jumping mechanics, including charge-based jumps.
- Collision detection with platforms, snow, trampolines, and other objects.
- Health system with visual health bar display.
- Animation system for walking, jumping, and falling states.
- Developer mode for free movement and debugging.
"""
class Player:
    def __init__(self, x, y, sounds):
        """
        Initialize the player with position, dimensions, velocities, and other attributes.

        Args:
            x (int): Initial x-coordinate of the player.
            y (int): Initial y-coordinate of the player.
            sounds (dict): Dictionary containing sound effects for various player actions.

        Returns:
            None
        """
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.color = BLUE
        self.x_velocity = 0
        self.y_velocity = 0
        self.grounded = False
        self.sounds = sounds
        self.jump_force = 10
        self.gravity = 0.8
        self.holding_jump = False
        self.jump_start_time = 0
        self.jump_allowed = True
        self.jump_direction = 0
        self.playing_fall_impact = False
        self.fall_start_time = None
        self.fall_duration_threshold = 0.6
        self.fall_counter = 0
        self.jump_count = 0
        self.on_ice = False
        self.has_landed = False
        self.max_health = 100
        self.current_health = 100
        self.health_bar_width = 50
        self.health_bar_image = pygame.transform.scale(
            pygame.image.load("assets/other/health_bar.png").convert_alpha(), (self.health_bar_width, 12)
        )

        self.walk_frames = []
        self.jump_charge_frame = None
        self.fall_frame = None

        self.current_walk_frame = 0
        self.walk_animation_speed = 0.1
        self.walk_animation_counter = 0

        self.update_skin(0)
        self.facing_right = True

    def handle_input(self, keys, current_level):
        """
        Handle user input for player movement and jumping.

        Args:
            keys (list): List of keys currently pressed.

        Returns:
            None
        """
        if self.playing_fall_impact:
            if keys[pygame.K_a] or keys[pygame.K_d]:
                self.playing_fall_impact = False
                self.image = self.walk_frames[0]
            if keys[pygame.K_SPACE]:
                self.playing_fall_impact = False
                self.jump(current_level)
            return

        if self.grounded and not self.holding_jump:
            if keys[pygame.K_a]:
                self.x_velocity = -3.5
                self.facing_right = False
            elif keys[pygame.K_d]:
                self.x_velocity = 3.5
                self.facing_right = True
            else:
                self.x_velocity = 0
        elif self.holding_jump:
            self.x_velocity = 0
            if keys[pygame.K_a]:
                self.jump_direction = -1
                self.facing_right = False
            elif keys[pygame.K_d]:
                self.jump_direction = 1
                self.facing_right = True
            else:
                self.jump_direction = 0

    def update_skin(self, selected_skin):
        """
        Update the player's skin based on the selected skin index.

        Args:
            selected_skin (int): Index of the selected skin.

        Returns:
            None
        """
        print("Selected skin:", selected_skin)
        prefix = "King_" if selected_skin == 1 else ""
        self.walk_frames = [
            pygame.transform.scale(pygame.image.load(os.path.join("assets/player_walk", f"{prefix}right{i}.png")).convert_alpha(), (self.width, self.height))
            for i in range(1, 3)
        ]
        self.jump_charge_frame = pygame.transform.scale(pygame.image.load(os.path.join("assets/player_jump", f"{prefix}jump.png")).convert_alpha(), (self.width, self.height))
        self.fall_frame = pygame.transform.scale(pygame.image.load(os.path.join("assets/player_fall", f"{prefix}fall.png")).convert_alpha(), (self.width, self.height))

        self.image = self.walk_frames[0]

    def start_jump(self):
        """
        Start charging a jump when the jump key is pressed.

        Returns:
            None
        """
        if self.grounded and self.jump_allowed:
            self.holding_jump = True
            self.jump_start_time = time.time()

    def release_jump(self, current_level):
        """
        Release the jump key and execute a jump based on the charged force.

        Args:
            current_level (int): The current level in the game to determine jump constraints.

        Returns:
            None
        """
        if self.holding_jump and self.jump_allowed:
            self.calculate_jump_force()
            self.jump(current_level)
            self.holding_jump = False
            self.jump_allowed = False

    def calculate_jump_force(self):
        """
        Calculate the jump force based on the duration the jump key was held.

        Returns:
            None
        """
        if self.jump_start_time:
            held_time = min(0.8, time.time() - self.jump_start_time)
            self.jump_force = 5 + held_time * 20

    def auto_jump(self, current_level):
        """
        Automatically execute a jump if the jump key is held for too long.

        Args:
            current_level (int): The current level in the game to determine jump constraints.

        Returns:
            None
        """
        if self.holding_jump and time.time() - self.jump_start_time >= 1.0:
            self.calculate_jump_force()
            self.jump(current_level)
            self.holding_jump = False
            self.jump_allowed = False

    def reset_jump(self):
        """
        Reset the jump state to allow the player to jump again.

        Returns:
            None
        """
        self.jump_allowed = True

    def jump(self, current_level):
        """
        Execute a jump with calculated velocity and apply jump direction.

        Args:
            current_level (int): The current level in the game to determine jump constraints.

        Returns:
            None
        """
        if self.grounded:
            self.jump_count += 1
            held_time = min(1.0, time.time() - self.jump_start_time)
            self.y_velocity = -self.jump_force
            max_speed = 7 if (
                current_level not in [17, 18] and (current_level != 19 or self.y >= 530)
            ) else 3
            min_speed = max_speed
            self.x_velocity = self.jump_direction * (max_speed - held_time * (max_speed - min_speed))
            self.grounded = False
            self.sounds["jump"].play()

    def apply_fall_damage(self, fall_duration):
        """
        Apply fall damage to the player based on the fall duration.

        Args:
            fall_duration (float): The duration of the player's fall.

        Returns:
            None
        """
        if fall_duration > 0.6:
            damage = min(self.max_health, int(12 * (fall_duration - 0.6)))
            self.current_health -= damage
            self.current_health = max(0, self.current_health)

    def draw_health_bar(self, screen):
        """
        Draw the health bar above the player.

        Args:
            screen (Surface): The pygame screen where the health bar is drawn.

        Returns:
            None
        """
        bar_x = self.x + (self.width // 2) - (self.health_bar_width // 2)
        bar_y = self.y - 22
        screen.blit(self.health_bar_image, (bar_x, bar_y))
        health_ratio = self.current_health / self.max_health
        top_rect = pygame.Rect(bar_x + 4, bar_y + 2, int(health_ratio * 44), 4)
        bottom_rect = pygame.Rect(bar_x + 4, bar_y + 6, int(health_ratio * 44), 4)
        pygame.draw.rect(screen, (214, 48, 40), top_rect)
        pygame.draw.rect(screen, (134, 25, 18), bottom_rect)

    def start_fall(self):
        """
        Start tracking the fall duration when the player begins falling.

        Returns:
            None
        """
        self.fall_start_time = time.time()

    def developer_mode(self, developer_mode):
        """
        Enable developer mode, allowing free movement without collision constraints.

        Args:
            developer_mode (bool): Whether developer mode is enabled.

        Returns:
            int: Always returns 0 to prevent normal updates in developer mode.
        """
        if developer_mode:
            self.grounded = False
            keys = pygame.key.get_pressed()
            self.y_velocity = 0
            self.x_velocity = 0

            if keys[pygame.K_w]:
                self.y -= 10
            if keys[pygame.K_s]:
                self.y += 10
            if keys[pygame.K_a]:
                self.x -= 10
            if keys[pygame.K_d]:
                self.x += 10
            return 0

    def handle_slope(self, platform, current_level, dy):
        """
        Handle slope interactions to modify velocity and position based on slope collision.

        Args:
            platform (Rect): The platform the player is interacting with.
            current_level (int): The current level in the game to determine slope behavior.
            dy (float): Vertical movement delta.

        Returns:
            float: Adjusted vertical movement delta after handling slopes.
        """
        if platform.width > 9:
            self.x_velocity = 0
        if platform.width < 9 and self.x > 561 and current_level == 16:
            self.x_velocity = -8
            self.y_velocity = 200
            dy = platform.top - self.height - self.y
        elif platform.width < 9 and self.x < 561 and current_level == 16:
            self.x_velocity = 8
            self.y_velocity = 200
            dy = platform.top - self.height - self.y
        elif platform.width < 9 and current_level == 14:
            self.x_velocity = -8
            self.y_velocity = 200
            dy = platform.top - self.height - self.y
        elif platform.width < 9 and current_level == 11 and self.x < 100:
            self.x_velocity = 8
            self.y_velocity = 200
            dy = platform.top - self.height - self.y
        elif platform.width < 9 and current_level == 11 and self.x > 100 and self.x < 388:
            self.x_velocity = -8
            self.y_velocity = 200
            dy = platform.top - self.height - self.y
        elif platform.width < 9 and current_level == 11 and self.x > 388:
            self.x_velocity = 8
            self.y_velocity = 200
            dy = platform.top - self.height - self.y
        else:
            dy = platform.top - self.height - self.y
            self.y_velocity = 0
            self.grounded = True
        return dy

    def check_collisions(self, platforms, dx, dy, current_level, game_instance):
        """
        Check for collisions with platforms and adjust the player's position and velocity accordingly.

        Args:
            platforms (list): List of platform Rect objects.
            dx (float): Horizontal movement delta.
            dy (float): Vertical movement delta.
            current_level (int): The current level in the game for special platform interactions.

        Returns:
            tuple: Adjusted horizontal (dx) and vertical (dy) movement deltas.
        """
        for platform in platforms:
            if platform.colliderect(self.x + dx, self.y, self.width, self.height):
                if not self.grounded:
                    self.sounds["bump"].play()
                dx = 0
                if self.facing_right:
                    self.x_velocity = -self.x_velocity + 3
                else:
                    self.x_velocity = -self.x_velocity - 3
            if platform.colliderect(self.x, self.y + dy, self.width, self.height):
                if self.y_velocity <= 0:
                    dy = platform.bottom - self.y
                    self.y_velocity = 0
                    self.sounds["bump"].play()
                elif self.y_velocity >= 0:
                    dy = self.handle_slope(platform, current_level, dy)
                    if self.fall_start_time:
                        fall_duration = time.time() - self.fall_start_time
                        if fall_duration >= self.fall_duration_threshold:
                            self.apply_fall_damage(fall_duration)
                            self.sounds["splat"].play()
                            self.playing_fall_impact = True
                            self.image = self.fall_frame
                            self.fall_counter += 1
                            if self.current_health <= 0:
                                game_instance.trigger_death()
                    
        return dx, dy

    def update(self, platforms, current_level, developer_mode, snow_rects_12, snow_rects_13, trampoline_rects, game_instance):
        """
        Update the player's state, including position, collisions, and fall handling.

        Args:
            platforms (list): List of platform Rect objects.
            current_level (int): The current level in the game.
            developer_mode (bool): Whether developer mode is enabled.
            snow_rects_12 (list): Snow Rect objects for level 12.
            snow_rects_13 (list): Snow Rect objects for level 13.
            trampoline_rects (list): Rects of trampolines for bounce interactions.

        Returns:
            int: Level transition indicator (1 for next level, -1 for previous level, 0 for no transition).
        """
        if self.y_velocity > 0 and not self.grounded:
            if self.fall_start_time is None:
                self.start_fall()
        else:
            self.fall_start_time = None

        if self.y < 0 and current_level < len(LEVEL_BACKGROUNDS) - 1:
            self.y = SCREEN_HEIGHT
            return 1
        if self.y > SCREEN_HEIGHT and current_level > 0:
            self.y = 0
            return -1

        if self.developer_mode(developer_mode) is not None:
            return 0

        dx = self.x_velocity
        dy = 0
        snow_rects = {12: snow_rects_12, 13: snow_rects_13}
        on_snow = any(
            current_level == level and any(snow.colliderect(self.x, self.y + dy, self.width, self.height) for snow in rects)
            for level, rects in snow_rects.items()
        )

        if on_snow:
            dx = 0

        self.gravity = 0.5 if (current_level == 17 or current_level == 18 or (current_level == 19 and self.y > 530)) else 0.8

        self.y_velocity += self.gravity
        if self.y_velocity > 15:
            self.y_velocity = 15
        dy += self.y_velocity

        for trampoline in trampoline_rects:
            if trampoline.colliderect(self.x, self.y + dy, self.width, self.height) and self.y_velocity > 0:
                self.y_velocity = -17
                dy = trampoline.top - self.height - self.y
                break

        if self.x + dx < 0:
            dx = 0
        elif self.x + self.width + dx > SCREEN_WIDTH:
            dx = 0

        was_grounded = self.grounded

        dx, dy = self.check_collisions(platforms, dx, dy, current_level, game_instance)

        if self.grounded and not was_grounded:
            if not self.has_landed:
                self.sounds["land"].play()
            self.has_landed = True
        elif not self.grounded:
            self.has_landed = False
        if self.y_velocity > 0.8:
            self.grounded = False

        self.y += dy
        self.x += dx

        self.auto_jump(current_level)
        return 0

    def draw(self, screen):
        """
        Draw the player on the screen, including animations for movement and falling.

        Args:
            screen (Surface): The pygame screen where the player is drawn.

        Returns:
            None
        """
        if self.playing_fall_impact:
            impact_frame = self.fall_frame
            if not self.facing_right:
                impact_frame = pygame.transform.flip(self.fall_frame, True, False)
            screen.blit(impact_frame, (self.x, self.y))
            return

        if self.grounded and self.x_velocity != 0:
            self.walk_animation_counter += self.walk_animation_speed
            if self.walk_animation_counter >= len(self.walk_frames):
                self.walk_animation_counter = 0
            self.current_walk_frame = int(self.walk_animation_counter)
            self.image = self.walk_frames[self.current_walk_frame]
        elif self.holding_jump:
            self.image = self.jump_charge_frame
        else:
            self.image = self.walk_frames[0]

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        screen.blit(self.image, (self.x, self.y))
