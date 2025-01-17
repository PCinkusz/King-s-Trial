import pygame
import time
import os
import sys
from player import Player
from constants import *
from levels import *
import json
"""
game_engine.py

This module implements the core game logic for the Jump King Recreation game.
It manages the game states, event handling, level rendering, and player interactions.

Features:
- Dynamic game state management (menu, gameplay, pause, ending).
- Timer-based gameplay with tracking of jumps, falls, and coins collected.
- Level rendering, including animations for snow, coins, and the flag.
- Menu navigation with options to continue, start a new game, or select skins.
- Saving and loading game progress and player statistics.
"""
class Game:
    def __init__(self):
        """
        Initialize the Game class with all necessary variables, assets, and configurations.

        Args:
            None

        Returns:
            None
        """
        pygame.display.set_caption("King's Trial")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"
        self.current_level = 0
        self.developer_mode = False
        self.snow_rects_level_13 = extract_platforms("assets/other/mapa13snieg.png")
        self.snow_rects_level_14 = extract_platforms("assets/other/mapa14snieg.png")
        self.trampoline_rects_level_12 = extract_platforms("assets/other/mapa12trampolina.png")
        self.bullets = []
        self.bullet_timer = 0
        self.bullet_spawn_interval = 2000
        self.snow_frame_index = 0
        self.snow_animation_timer = 0
        self.start_time = 0
        self.is_paused = False
        self.pause_selected_option = 0
        self.paused_time_start = 0
        self.pause_options = ["RESUME", "SAVE & EXIT", "GIVE UP"]
        self.main_menu_options = ["CONTINUE", "SKINS", "QUIT"]
        self.main_menu_selected_option = 0
        self.has_save_game = os.path.exists("savegame.json")
        self.is_skin_unlocked = False
        self.in_skin_selection = False
        self.main_menu_selected_option = 0
        self.selected_skin = 0
        self.flag_position = (700, 130)
        self.flag_raised = False
        self.flag_moving = False
        self.flag_raised_time = None
        self.timer_stopped = False
        self.final_time = None
        self.show_ending_stats = False
        self.best_time = None
        self.flag_image = pygame.transform.scale(pygame.image.load("assets/other/flag.png").convert_alpha(), (85, 50))
        pygame.mixer.init()
        self.sounds = {
            "bump": pygame.mixer.Sound("assets/sounds/bump_sound.wav"),
            "jump": pygame.mixer.Sound("assets/sounds/jump_sound.wav"),
            "land": pygame.mixer.Sound("assets/sounds/land_sound.wav"),
            "splat": pygame.mixer.Sound("assets/sounds/splat_sound.wav"),
            "select": pygame.mixer.Sound("assets/sounds/select_sound.wav"),
        }
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60, self.sounds)
        pygame.mixer.music.load("assets/sounds/menu_intro.wav")
        pygame.mixer.music.play(-1)
        for sound in self.sounds.values():
            sound.set_volume(0.07)

        pygame.mixer.music.set_volume(0.07)
        self.available_skins = [
            "assets/player_walk/Right1.png",
            "assets/player_walk/King_right1.png",
        ]

        self.animated_snow = [
            pygame.transform.scale(pygame.image.load(
                os.path.join("assets/snowAni", f"snowAnimation{i}.png")
            ).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            for i in range(1, 9)
        ]
        self.cursor_image = pygame.transform.scale(
            pygame.image.load("assets/gui/cursor.png").convert_alpha(), (30, 30)
        )

        self.coin_frames = [
            pygame.transform.scale(pygame.image.load(os.path.join("assets/coin", f"coin{i}.png")).convert_alpha(), (50, 50))
            for i in range(1, 7)
        ]
        self.coins = [
            {"pos": (506, 175), "level": 0, "collected": False, "frame_index": 0, "fx_frame_index": 0, "show_fx": False},
            {"pos": (753, 60), "level": 3, "collected": False, "frame_index": 0, "fx_frame_index": 0, "show_fx": False},
            {"pos": (560, 338), "level": 5, "collected": False, "frame_index": 0, "fx_frame_index": 0, "show_fx": False},
            {"pos": (215, 649), "level": 8, "collected": False, "frame_index": 0, "fx_frame_index": 0, "show_fx": False},
            {"pos": (309, 558), "level": 12, "collected": False, "frame_index": 0, "fx_frame_index": 0, "show_fx": False},
            {"pos": (755, 474), "level": 14, "collected": False, "frame_index": 0, "fx_frame_index": 0, "show_fx": False},
            {"pos": (0, 355), "level": 18, "collected": False, "frame_index": 0, "fx_frame_index": 0, "show_fx": False},
            {"pos": (592, 521), "level": 20, "collected": False, "frame_index": 0, "fx_frame_index": 0, "show_fx": False}
        ]
        self.coin_animation_speed = 0.1
        self.total_coins_collected = 0
        self.coin_collect_frames = [
            pygame.transform.scale(pygame.image.load(os.path.join("assets/coin_collect", f"SP103_0{i}.png")).convert_alpha(), (64, 64))
            for i in range(1, 5)
        ]

        self.font_path = "assets/fonts/ttf_alkhemikal.ttf"
        self.font_size = 60
        self.load_progress()

    def get_font(self, size):
        """
        Load and return a specific font size for use in UI elements.

        Args:
            size (int): The font size to be loaded.

        Returns:
            Font: Pygame font object for the given size.
        """
        return pygame.font.Font(self.font_path, size)

    def animate_coin_collect_fx(self):
        """
        Animate the visual effects of coins being collected.

        Args:
            None

        Returns:
            None
        """
        for coin in self.coins:
            if coin["show_fx"]:
                if coin["fx_frame_index"] < len(self.coin_collect_frames):
                    fx_frame = self.coin_collect_frames[int(coin["fx_frame_index"])]
                    fx_x = coin["pos"][0] - (64 - 50) // 2
                    fx_y = coin["pos"][1] - (64 - 50) // 2
                    self.screen.blit(fx_frame, (fx_x, fx_y))
                    coin["fx_frame_index"] += 0.3
                else:
                    coin["show_fx"] = False

    def check_coin_collection(self):
        """
        Check for coin collection by the player and update the game state accordingly.

        Args:
            None

        Returns:
            None
        """
        if self.is_skin_unlocked:
            return

        for coin in self.coins:
            if not coin["collected"] and coin["level"] == self.current_level:
                coin_rect = pygame.Rect(coin["pos"][0], coin["pos"][1], 32, 32)
                player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                if player_rect.colliderect(coin_rect):
                    coin["collected"] = True
                    coin["show_fx"] = True
                    self.total_coins_collected += 1

                    if self.total_coins_collected == len(self.coins):
                        print("All coins collected")
                        self.is_skin_unlocked = True
                        self.save_progress()

    def animate_snow(self):
        """
        Animate falling snow for certain levels to create a dynamic visual effect.

        Args:
            None

        Returns:
            None
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.snow_animation_timer > 300:
            self.snow_animation_timer = current_time
            self.snow_frame_index = (self.snow_frame_index + 1) % len(self.animated_snow)

        snow_image = self.animated_snow[self.snow_frame_index]
        self.screen.blit(snow_image, (0, 0))

    def trigger_death(self):
        """
        Handle player death by resetting relevant game states and deleting the save file.

        Args:
            None

        Returns:
            None
        """
        self.state = "death"
        self.player.current_health = 0
        self.start_time = 0

        save_path = "savegame.json"
        if os.path.exists(save_path):
            os.remove(save_path)
        print("Player died. Save file deleted.")

    def draw_jump_bar(self):
        """
        Draw a jump charge bar to indicate how much the player is charging their jump.

        Args:
            None

        Returns:
            None
        """
        bar_width = 150
        bar_height = 20
        padding = 10
        max_charge_time = 1.0
        charge_ratio = 0

        if self.player.holding_jump:
            held_time = min(max_charge_time, time.time() - self.player.jump_start_time)
            charge_ratio = held_time / max_charge_time

        bar_x = SCREEN_WIDTH - bar_width - padding
        bar_y = SCREEN_HEIGHT - bar_height - padding
        fill_width = int(bar_width * charge_ratio)

        bar_color = (0, 255, 0) if charge_ratio < 0.5 else (255, 255, 0)

        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

    def start_game(self):
        """
        Switch the game state to gameplay when the game starts.

        Args:
            None

        Returns:
            None
        """
        self.state = "gameplay"

    def start_new_game(self):
        """
        Reset the game to its initial state for a new game session.

        Args:
            None

        Returns:
            None
        """
        self.player.x, self.player.y = SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60
        self.player.current_health = 100
        self.current_level = 0
        self.start_time = time.time()
        self.paused_time_start = 0
        self.total_coins_collected = 0
        self.player.jump_count = 0
        self.player.fall_counter = 0
        self.flag_raised = False
        self.flag_moving = False
        self.timer_stopped = False
        #self.flag_raised_time = None
        self.final_time = None
        for coin in self.coins:
            coin["collected"] = False
            coin["show_fx"] = False
            coin["fx_frame_index"] = 0
        self.state = "gameplay"

    def show_menu(self):
        """
        Render the main menu screen with all menu options and visual elements.

        Args:
            None

        Returns:
            None
        """
        self.screen.fill(WHITE)
        font = self.get_font(60)
        text = font.render("Press SPACE to Start", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def draw_level(self):
        """
        Render the current level, including the background, player, platforms, coins, and snow animations.

        Args:
            None

        Returns:
            None
        """
        self.screen.blit(LEVEL_BACKGROUNDS[self.current_level], (0, 0))
        if self.current_level == 8:
            for bullet in self.bullets:
                pygame.draw.rect(self.screen, (255, 0, 0), bullet)

        if self.current_level == 12:
            self.player.draw(self.screen)
            self.animate_snow()
            self.screen.blit(pygame.transform.scale(pygame.image.load("assets/background/mapa13samsnieg.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        elif self.current_level == 13:
            self.player.draw(self.screen)
            self.animate_snow()
            self.screen.blit(pygame.transform.scale(pygame.image.load("assets/background/mapa14samsnieg.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        else:
            self.player.draw(self.screen)

        self.player.draw_health_bar(self.screen)

        if not self.is_skin_unlocked:
            for coin in self.coins:
                if not coin["collected"] and coin["level"] == self.current_level:
                    frame_index = int(coin["frame_index"]) % len(self.coin_frames)
                    coin_image = self.coin_frames[frame_index]
                    self.screen.blit(coin_image, coin["pos"])

                    coin["frame_index"] += self.coin_animation_speed
            self.animate_coin_collect_fx()

    def draw_timer(self):
        """
        Display an in-game timer, formatted to show hours, minutes, and seconds dynamically.

        Args:
            None

        Returns:
            None
        """
        if self.timer_stopped:
            elapsed_time = time.time() - self.start_time
            return
        if self.start_time > 0:
            if not self.is_paused:
                elapsed_time = time.time() - self.start_time
            else:
                elapsed_time = self.paused_time_start - self.start_time
        else:
            elapsed_time = 0

        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        timer_text = f"{hours:02}:{minutes:02}:{seconds:02}"
        font = self.get_font(30)
        timer_surface = font.render(timer_text, True, WHITE)
        self.screen.blit(timer_surface, (20, 20))

    def draw_death_screen(self):
        """
        Draw the death screen with a restart message when the player dies.

        Args:
            None

        Returns:
            None
        """
        font = self.get_font(150)
        font2 = self.get_font(30)
        death_message = font.render("YOU DIED", True, WHITE)
        restart_message = font2.render("Press SPACE to start over", True, WHITE)
        self.screen.blit(death_message, (SCREEN_WIDTH // 2 - death_message.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(restart_message, (SCREEN_WIDTH // 2 - restart_message.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.start_new_game()

    def draw_main_menu(self):
        """
        Render the main menu screen, including skin selection and best time display.

        Args:
            None

        Returns:
            None
        """
        self.screen.fill(BLACK)
        if self.in_skin_selection:
            self.draw_skins_in_main_menu()
        font = self.get_font(30)

        logo = pygame.image.load("assets/gui/logo.png").convert_alpha()
        self.screen.blit(logo, (SCREEN_WIDTH // 2 - logo.get_width() // 2, 100))

        frame_rect = pygame.Rect(20, 450, 260, 300)
        main_menu_frame = pygame.image.load("assets/gui/frame_main_menu.png").convert_alpha()
        self.screen.blit(main_menu_frame, frame_rect.topleft)

        for i, option in enumerate(self.main_menu_options):
            if option == "CONTINUE" and not self.has_save_game:
                option = "NEW GAME"

            color = WHITE if i == self.main_menu_selected_option else (200, 200, 200)
            text_surface = font.render(option, True, color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (
                frame_rect.left + 70 + (10 if self.main_menu_selected_option == i else 0),
                frame_rect.top + 70 + i * (text_rect.height + 30)
            )
            self.screen.blit(text_surface, text_rect)

            if i == self.main_menu_selected_option:
                cursor_x = text_rect.left - 40
                cursor_y = text_rect.centery - self.cursor_image.get_height() // 2
                self.screen.blit(self.cursor_image, (cursor_x, cursor_y))
        font2 = self.get_font(20)
        if self.best_time is not None:
            hours = int(self.best_time // 3600)
            minutes = int((self.best_time % 3600) // 60)
            seconds = int(self.best_time % 60)
            if hours > 0:
                best_time_text = f"Best Time: {hours}h {minutes}m {seconds}s"
            else:
                best_time_text = f"Best Time: {minutes}m {seconds}s"
        else:
            best_time_text = "Best Time: N/A"
        best_time_surface = font2.render(best_time_text, True, WHITE)
        self.screen.blit(best_time_surface, (SCREEN_WIDTH // 2 - best_time_surface.get_width() // 2, SCREEN_HEIGHT - 30))

    def draw_skins_in_main_menu(self):
        """
        Render the skin selection screen in the main menu, showing available and locked skins.

        Args:
            None

        Returns:
            None
        """
        frame_rect = pygame.Rect(400, 450, 300, 200)
        main_menu_frame = pygame.transform.scale(
            pygame.image.load("assets/gui/frame_main_menu.png").convert_alpha(),
            (frame_rect.width, frame_rect.height)
        )
        self.screen.blit(main_menu_frame, frame_rect.topleft)

        for i, option in enumerate(self.available_skins):
            skin_image = pygame.transform.scale(pygame.image.load(option).convert_alpha(), (100, 100))
            skin_rect = skin_image.get_rect()
            skin_rect.topleft = (frame_rect.left + 30 + i * (skin_rect.height + 30), frame_rect.top + 40 + (0 if self.selected_skin == i else 10))

            if i == 1 and not self.is_skin_unlocked:
                gray_skin = pygame.Surface(skin_image.get_size(), flags=pygame.SRCALPHA)
                gray_skin.fill((0, 0, 0, 150))
                skin_image.blit(gray_skin, (0, 0))
                lock_icon = pygame.image.load("assets/gui/locked.png").convert_alpha()
                lock_icon = pygame.transform.scale(lock_icon, (120, 120))
                lock_rect = lock_icon.get_rect(center=skin_rect.center)
                self.screen.blit(skin_image, skin_rect.topleft)
                self.screen.blit(lock_icon, lock_rect.topleft)
            else:
                self.screen.blit(skin_image, skin_rect)

            if i == self.selected_skin:
                cursor_x = skin_rect.centerx - (self.cursor_image.get_width() // 2)
                cursor_y = skin_rect.bottom + 10
                rotated_cursor = pygame.transform.rotate(self.cursor_image, 90)
                self.screen.blit(rotated_cursor, (cursor_x, cursor_y))

    def draw_pause_screen(self):
        """
        Draw the pause menu with options to resume, save & exit, or give up.

        Args:
            None

        Returns:
            None
        """
        pause_rect = pygame.Rect(SCREEN_WIDTH - 280, 20, 260, 240)
        main_frame = pygame.image.load("assets/gui/frame_main.png").convert_alpha()
        self.screen.blit(main_frame, pause_rect.topleft)

        font = self.get_font(30)
        for i, option in enumerate(self.pause_options):
            color = WHITE if i == self.pause_selected_option else (200, 200, 200)
            text_surface = font.render(option, True, color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (pause_rect.left + 60 + (10 if i == self.pause_selected_option else 0), 70 + i * (text_rect.height + 20))
            self.screen.blit(text_surface, text_rect)

            if i == self.pause_selected_option:
                cursor_x = text_rect.left - 20 - self.cursor_image.get_width()
                cursor_y = text_rect.centery - 5 - self.cursor_image.get_height() // 2
                self.screen.blit(self.cursor_image, (cursor_x, cursor_y))

        info_rect = pygame.Rect(20, 20, 306, 167)
        info_frame = pygame.image.load("assets/gui/frame_info.png").convert_alpha()
        self.screen.blit(info_frame, info_rect.topleft)

        if self.start_time > 0:
            if self.is_paused and self.paused_time_start > 0:
                elapsed_time = self.paused_time_start - self.start_time
            else:
                elapsed_time = time.time() - self.start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
        else:
            hours, minutes, seconds = 0, 0

        jumps = self.player.jump_count
        falls = self.player.fall_counter

        info_texts = [
            f"TIME : {hours}h {minutes}m {seconds}s",
            f"JUMPS : {jumps}",
            f"FALLS : {falls}"
        ]
        for i, text in enumerate(info_texts):
            text_surface = font.render(text, True, WHITE)
            self.screen.blit(text_surface, (info_rect.x + 60, info_rect.y + 30 + i * 40))

    def toggle_pause(self):
        """
        Toggle the pause state of the game and adjust game timing accordingly.

        Args:
            None

        Returns:
            None
        """
        self.is_paused = not self.is_paused
        if self.is_paused:
            pygame.mixer.music.pause()
            self.pause_selected_option = 0
            self.paused_time_start = time.time()
        else:
            pygame.mixer.music.unpause()
            if self.paused_time_start > 0:
                paused_duration = time.time() - self.paused_time_start
                self.start_time += paused_duration
                self.paused_time_start = 0

    def handle_main_menu_input(self, event):
        """
        Handle player input in the main menu, including navigation and selection of menu options.

        Args:
            event (Event): The Pygame event object.

        Returns:
            None
        """
        if event.type == pygame.KEYDOWN:
            if self.in_skin_selection:
                if event.key == pygame.K_a:
                    self.selected_skin = (self.selected_skin - 1) % len(self.available_skins)
                elif event.key == pygame.K_d:
                    self.selected_skin = (self.selected_skin + 1) % len(self.available_skins)
                elif event.key == pygame.K_RETURN:
                    self.sounds["select"].play()
                    self.player.image = pygame.image.load(self.available_skins[self.selected_skin]).convert_alpha()
                    if self.selected_skin == 1 and not self.is_skin_unlocked:
                        print("This skin is locked!")
                    else:
                        self.player.update_skin(self.selected_skin)
                        self.in_skin_selection = False

                elif event.key == pygame.K_ESCAPE:
                    self.sounds["select"].play()
                    self.in_skin_selection = False
            else:
                if event.key == pygame.K_w:
                    self.main_menu_selected_option = (self.main_menu_selected_option - 1) % len(self.main_menu_options)
                elif event.key == pygame.K_s:
                    self.main_menu_selected_option = (self.main_menu_selected_option + 1) % len(self.main_menu_options)
                elif event.key == pygame.K_RETURN:
                    self.sounds["select"].play()
                    selected_option = self.main_menu_options[self.main_menu_selected_option]
                    if selected_option == "SKINS":
                        self.in_skin_selection = True
                    elif selected_option == "CONTINUE" and self.has_save_game:
                        self.load_save()
                        self.state = "gameplay"
                    elif selected_option == "CONTINUE" and not self.has_save_game or selected_option == "NEW GAME":
                        self.start_new_game()
                    elif selected_option == "QUIT":
                        pygame.quit()
                        sys.exit()

    def handle_pause_input(self, event):
        """
        Handle player input in the pause menu, allowing navigation and selection of options.

        Args:
            event (Event): The Pygame event object.

        Returns:
            None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle_pause()
            elif event.key == pygame.K_w:
                self.pause_selected_option = (self.pause_selected_option - 1) % len(self.pause_options)
            elif event.key == pygame.K_s:
                self.pause_selected_option = (self.pause_selected_option + 1) % len(self.pause_options)
            elif event.key == pygame.K_RETURN:
                self.handle_pause_selection()

    def handle_pause_selection(self):
        """
        Perform actions based on the currently selected pause menu option.

        Args:
            None

        Returns:
            None
        """
        selected_option = self.pause_options[self.pause_selected_option]
        if selected_option == "RESUME":
            self.toggle_pause()
        elif selected_option == "SAVE & EXIT":
            self.save_and_exit()
        elif selected_option == "GIVE UP":
            self.give_up()

    def save_and_exit(self):
        """
        Save the current game state (position, level, and other data) to a file and exit the game.

        Args:
            None

        Returns:
            None
        """
        if self.start_time > 0:
            elapsed_time = time.time() - self.start_time
        else:
            elapsed_time = 0
        save_data = {
            "player_x": self.player.x,
            "player_y": self.player.y,
            "current_level": self.current_level,
            "elapsed_time": elapsed_time,
            "current_health": self.player.current_health,
            "jumps": self.player.jump_count,
            "falls": self.player.fall_counter,
            "total_coins_collected": self.total_coins_collected,
            "coins": [coin["collected"] for coin in self.coins]
        }
        save_path = "savegame.json"
        try:
            with open(save_path, 'w') as save_file:
                json.dump(save_data, save_file, indent=4)
            print(f"Game saved successfully at {save_path}")
        except Exception as e:
            print(f"Failed to save game: {e}")

        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()

    def save_progress(self):
        """
        Save progress data, such as unlocked skins and the best time, to a progress file.

        Args:
            None

        Returns:
            None
        """
        progress_data = {
            "is_skin_unlocked": self.is_skin_unlocked,
            "best_time": self.best_time
        }

        progress_path = "progress.json"
        try:
            with open(progress_path, 'w') as progress_file:
                json.dump(progress_data, progress_file, indent=4)
            print(f"Progress saved successfully at {progress_path}")
        except Exception as e:
            print(f"Failed to save progress: {e}")

    def load_progress(self):
        """
        Load progress data, including the best time and skin unlock status, from a file.

        Args:
            None

        Returns:
            None
        """
        progress_path = "progress.json"
        if os.path.exists(progress_path):
            try:
                with open(progress_path, 'r') as progress_file:
                    progress_data = json.load(progress_file)
                    self.is_skin_unlocked = progress_data.get("is_skin_unlocked", False)
                    self.best_time = progress_data.get("best_time", None)
                    print("Progress loaded successfully!")
            except Exception as e:
                print(f"Failed to load progress: {e}")
        else:
            self.is_skin_unlocked = False
            self.best_time = None

    def give_up(self):
        """
        Handle the "give up" option by deleting the save file and exiting the game.

        Args:
            None

        Returns:
            None
        """
        save_path = "savegame.json"
        if os.path.exists(save_path):
            os.remove(save_path)
            print("Save file deleted. Starting a new game next time.")
        else:
            print("No save file to delete.")
        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()

    def load_save(self):
        """
        Load a saved game state from a file and apply it to the current game session.

        Args:
            None

        Returns:
            None
        """
        save_path = "savegame.json"
        if os.path.exists(save_path):
            with open(save_path, 'r') as save_file:
                save_data = json.load(save_file)
                self.player.x = save_data["player_x"]
                self.player.y = save_data["player_y"]
                self.current_level = save_data["current_level"]
                self.player.current_health = save_data["current_health"]
                self.start_time = time.time() - save_data["elapsed_time"]
                self.player.jump_count = save_data.get("jumps", 0)
                self.player.fall_counter = save_data.get("falls", 0)
                self.total_coins_collected = save_data.get("total_coins_collected", 0)
                saved_coins = save_data.get("coins", [False] * len(self.coins))
                for i, coin in enumerate(self.coins):
                    coin["collected"] = saved_coins[i] if i < len(saved_coins) else False
                print("Game loaded successfully!")

    def animate_flag(self):
        """
        Animate the flag being raised and update the best time if necessary.

        Args:
            None

        Returns:
            None
        """
        if self.flag_moving:
            current_x, current_y = self.flag_position
            if current_y > 30:
                self.flag_position = (current_x, current_y - 2)
            else:
                self.flag_moving = False
                self.flag_raised = True
                self.flag_raised_time = time.time()
                self.timer_stopped = True
                self.final_time = self.flag_raised_time - self.start_time
                if self.best_time is None:
                    self.best_time = self.final_time
                    self.save_progress()
                elif self.final_time < self.best_time:
                    self.best_time = self.final_time
                    self.save_progress()

            self.screen.blit(self.flag_image, self.flag_position)

        if self.flag_raised:
            font = self.get_font(40)
            victory_text = font.render("The kingdom is restored. The flag waves high!", True, BLACK)
            self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2))
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.start_time = time.time()
                self.state = "ending"

    def draw_ending_screen(self):
        """
        Render the ending screen with statistics and a congratulatory message when the game is completed.

        Args:
            None

        Returns:
            None
        """
        self.screen.fill(BLACK)
        font = self.get_font(50)
        font_small = self.get_font(30)

        title = font.render("Congratulations!", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        elapsed_time = self.final_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)

        stats = [
            f"Time: {hours}h {minutes}m {seconds}s",
            f"Jumps: {self.player.jump_count}",
            f"Falls: {self.player.fall_counter}",
        ]
        for i, stat in enumerate(stats):
            stat_text = font_small.render(stat, True, WHITE)
            self.screen.blit(stat_text, (SCREEN_WIDTH // 2 - stat_text.get_width() // 2, 250 + i * 50))

        instruction = font_small.render("Press SPACE to return to Main Menu", True, WHITE)
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 500))

    def run_gameplay(self):
        """
        Handle the core gameplay logic, including rendering the level, updating the player, and handling interactions.

        Args:
            None

        Returns:
            None
        """
        if self.state == "death":
            self.draw_death_screen()
            return
        if self.is_paused:
            self.draw_pause_screen()
            return

        self.draw_level()
        keys = pygame.key.get_pressed()
        platforms = LEVEL_PLATFORMS[self.current_level]
        trampoline_rects = self.trampoline_rects_level_12 if self.current_level == 11 else []
        level_change = self.player.update(
            platforms, self.current_level, self.developer_mode,
            self.snow_rects_level_13, self.snow_rects_level_14,
            trampoline_rects, self
        )

        if self.start_time <= 0 and self.player.jump_start_time > 0:
            self.start_time = time.time()

        current_time = pygame.time.get_ticks()
        if current_time - self.bullet_timer >= self.bullet_spawn_interval and self.current_level == 8:
            self.bullet_timer = current_time
            bullet_rect = pygame.Rect(63, 664, 20, 7)
            self.bullets.append(bullet_rect)
        for bullet in self.bullets[:]:
            bullet.x += 5
            if bullet.x > SCREEN_WIDTH:
                self.bullets.remove(bullet)

            if bullet.colliderect(self.player.x, self.player.y, self.player.width, self.player.height):
                print("Player hit by bullet!")
                self.player.grounded = False
                self.player.x_velocity = 10
                self.player.y_velocity = -5
                self.bullets.remove(bullet)

        if level_change == 1 and self.current_level < len(LEVEL_BACKGROUNDS) - 1:
            self.current_level += 1
        elif level_change == -1 and self.current_level > 0:
            self.current_level -= 1

        if self.current_level == len(LEVEL_BACKGROUNDS) - 1:
            pole_rect = pygame.Rect(769, 146, 10, 100)
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            if player_rect.colliderect(pole_rect) and not self.flag_raised:
                self.flag_moving = True
            self.animate_flag()

        self.player.handle_input(keys, self.current_level)
        self.draw_jump_bar()
        self.draw_timer()

    def handle_events(self):
        """
        Process player inputs and other events, such as quitting, pausing, and navigating menus.

        Args:
            None

        Returns:
            None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_and_exit()

            if self.state == "ending" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.state = "menu"
                    self.has_save_game = False
                    save_path = "savegame.json"
                    if os.path.exists(save_path):
                        os.remove(save_path)

            if self.state == "menu" and event.type == pygame.KEYDOWN:
                self.handle_main_menu_input(event)

            if self.state == "gameplay":
                if self.is_paused:
                    self.handle_pause_input(event)
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and not self.developer_mode:
                            self.player.start_jump()
                        if event.key == pygame.K_ESCAPE:
                            self.toggle_pause()
                        if event.key == pygame.K_u:
                            self.developer_mode = not self.developer_mode
                            print(f"Developer Mode: {'ON' if self.developer_mode else 'OFF'}")

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.player.release_jump(self.current_level)
                        self.player.reset_jump()

    def update(self):
        """
        Update the game state based on the current mode (menu, gameplay, or ending).

        Args:
            None

        Returns:
            None
        """
        if self.state == "menu":
            self.draw_main_menu()
        elif self.state == "gameplay":
            self.run_gameplay()
            self.check_coin_collection()
        elif self.state == "ending":
            self.draw_ending_screen()

    def run(self):
        """
        Run the main game loop, which processes events, updates the game state, and renders the screen.

        Args:
            None

        Returns:
            None
        """
        self.load_save()
        while self.running:
            self.handle_events()
            if self.state == "death":
                self.run_gameplay()
            else:
                self.update()
            pygame.display.flip()
            self.clock.tick(FPS)
