import pygame
import random
from .target import Target
from .sound_manager import SoundManager

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)
MUTED = (190, 190, 195)


class GameEngine:
    # Target settings: (base radius, minimum radius, lifespan in frames)
    DIFFICULTIES = {
        "Easy": (50, 18, 120),
        "Medium": (40, 12, 90),
        "Hard": (30, 8, 60),
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60
        self.round_seconds = 30

        self.font = pygame.font.SysFont("Arial", 26)
        self.game_over_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.game_over_detail_font = pygame.font.SysFont("Arial", 28)
        self.game_over_message_font = pygame.font.SysFont("Arial", 22)
        self.menu_title_font = pygame.font.SysFont("Arial", 42, bold=True)
        self.menu_option_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.menu_help_font = pygame.font.SysFont("Arial", 20)

        self.sound = SoundManager()
        self.difficulty = "Medium"
        self.menu_active = False
        self.game_over = False
        self.quit_requested = False
        self._start_new_game(self.difficulty)

    def _target_settings(self):
        return self.DIFFICULTIES[self.difficulty]

    def _spawn_target(self):
        x = random.randint(self.margin, self.width - self.margin)
        y = random.randint(self.margin + self.hud_height, self.height - self.margin)
        base_radius, min_radius, lifespan_frames = self._target_settings()
        return Target(
            x,
            y,
            base_radius=base_radius,
            min_radius=min_radius,
            lifespan_frames=lifespan_frames,
        )

    def _start_new_game(self, difficulty):
        self.difficulty = difficulty
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.time_left_frames = self.round_seconds * 60
        self.game_over = False
        self.menu_active = False
        self.sound.stop_all()
        self.target = self._spawn_target()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.game_over and not self.menu_active:
                # A click on the results screen advances to the menu.
                self.menu_active = True
            elif self.menu_active:
                self._handle_menu_click(event.pos)
            elif not self.game_over:
                self._handle_click(event.pos)

    def _handle_keydown(self, key):
        if self.menu_active:
            if key == pygame.K_1:
                self._start_new_game("Easy")
            elif key == pygame.K_2:
                self._start_new_game("Medium")
            elif key == pygame.K_3:
                self._start_new_game("Hard")
            elif key in (pygame.K_ESCAPE, pygame.K_q):
                self.quit_requested = True
        elif self.game_over:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.menu_active = True
            elif key in (pygame.K_ESCAPE, pygame.K_q):
                self.quit_requested = True

    def _menu_option_rects(self):
        option_width = min(360, self.width - 80)
        option_height = 54
        gap = 14
        start_y = self.height // 2 - 65
        return {
            name: pygame.Rect(
                (self.width - option_width) // 2,
                start_y + index * (option_height + gap),
                option_width,
                option_height,
            )
            for index, name in enumerate(("Easy", "Medium", "Hard"))
        }

    def _handle_menu_click(self, pos):
        for name, rect in self._menu_option_rects().items():
            if rect.collidepoint(pos):
                self._start_new_game(name)
                return

        if self._exit_menu_rect().collidepoint(pos):
            self.quit_requested = True

    def _exit_menu_rect(self):
        text = self.menu_help_font.render("Exit game", True, WHITE)
        return text.get_rect(center=(self.width // 2, self.height - 48)).inflate(36, 18)

    def _handle_click(self, pos):
        x, y = pos
        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.sound.play("hit")
            self.target = self._spawn_target()
        else:
            self.misses += 1
            self.sound.play("click_miss")

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is mouse-driven.
        pass

    def update(self):
        if self.game_over or self.menu_active or self.quit_requested:
            return

        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.time_left_frames = 0
            self.game_over = True
            self.sound.play("game_over")
            return

        self.target.update()
        if self.target.expired():
            self.misses += 1
            self.sound.play("timeout_miss")
            self.target = self._spawn_target()

    def accuracy(self):
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(100 * self.hits / total, 1)

    def _render_game_over(self, screen):
        title = self.game_over_font.render("GAME OVER", True, WHITE)
        score = self.game_over_detail_font.render(
            f"Final Score: {self.score}", True, WHITE
        )
        accuracy = self.game_over_detail_font.render(
            f"Final Accuracy: {self.accuracy()}%", True, WHITE
        )
        message = self.game_over_message_font.render(
            "Press ENTER or click to choose a difficulty", True, MUTED
        )
        exit_message = self.menu_help_font.render(
            "Press ESC or Q to exit", True, MUTED
        )

        screen.blit(title, title.get_rect(center=(self.width // 2, self.height // 2 - 100)))
        screen.blit(score, score.get_rect(center=(self.width // 2, self.height // 2 - 25)))
        screen.blit(accuracy, accuracy.get_rect(center=(self.width // 2, self.height // 2 + 20)))
        screen.blit(message, message.get_rect(center=(self.width // 2, self.height // 2 + 95)))
        screen.blit(exit_message, exit_message.get_rect(center=(self.width // 2, self.height - 28)))

    def _render_menu(self, screen):
        title = self.menu_title_font.render("SELECT DIFFICULTY", True, WHITE)
        subtitle = self.menu_help_font.render(
            "Choose with mouse or press 1, 2, or 3", True, MUTED
        )
        screen.blit(title, title.get_rect(center=(self.width // 2, 85)))
        screen.blit(subtitle, subtitle.get_rect(center=(self.width // 2, 135)))

        descriptions = {
            "Easy": "Larger targets  |  Longer lifespan",
            "Medium": "Default target size and lifespan",
            "Hard": "Smaller targets  |  Shorter lifespan",
        }
        for name, rect in self._menu_option_rects().items():
            pygame.draw.rect(screen, (65, 65, 75), rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=8)
            label = self.menu_option_font.render(f"{name}  ({('1' if name == 'Easy' else '2' if name == 'Medium' else '3')})", True, WHITE)
            screen.blit(label, label.get_rect(center=(rect.centerx, rect.centery - 8)))
            detail = self.menu_help_font.render(descriptions[name], True, MUTED)
            screen.blit(detail, detail.get_rect(center=(rect.centerx, rect.centery + 17)))

        exit_label = self.menu_help_font.render("Exit game", True, WHITE)
        screen.blit(exit_label, exit_label.get_rect(center=(self.width // 2, self.height - 48)))

    def render(self, screen):
        if self.menu_active:
            self._render_menu(screen)
            return

        if self.game_over:
            self._render_game_over(screen)
            return

        r = int(self.target.visual_radius())
        pygame.draw.circle(screen, RED, (self.target.x, self.target.y), r)
        pygame.draw.circle(screen, WHITE, (self.target.x, self.target.y), r, 2)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        seconds_left = max(0, self.time_left_frames // 60)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (self.width - 140, 10))

        acc_text = self.font.render(f"Accuracy: {self.accuracy()}%", True, WHITE)
        screen.blit(acc_text, (self.width // 2 - 90, 10))
