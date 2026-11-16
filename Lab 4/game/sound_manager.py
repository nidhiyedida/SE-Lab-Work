"""Small, local sound-effect manager for the Target Aim Trainer."""

from pathlib import Path
import pygame


class SoundManager:
    """Loads optional local WAV effects and plays them on dedicated channels."""

    SOUND_FILES = {
        "hit": "hit.wav",
        "click_miss": "click_miss.wav",
        "timeout_miss": "timeout_miss.wav",
        "game_over": "game_over.wav",
    }

    CHANNELS = {
        "hit": 0,
        "click_miss": 1,
        "timeout_miss": 1,  # Replaces an earlier miss sound instead of stacking.
        "game_over": 2,
    }

    def __init__(self):
        self.sounds = {}
        self.channels = {}
        self.enabled = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(max(pygame.mixer.get_num_channels(), 3))
            self.enabled = True
        except pygame.error:
            # Audio is optional: the game remains fully playable without it.
            return

        sound_dir = Path(__file__).resolve().parent / "assets" / "sounds"
        for name, filename in self.SOUND_FILES.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(str(sound_dir / filename))
                self.sounds[name].set_volume(0.55)
            except (pygame.error, OSError):
                # Missing or invalid individual assets should not stop the game.
                continue

        for name, channel_index in self.CHANNELS.items():
            self.channels[name] = pygame.mixer.Channel(channel_index)

    def play(self, name):
        if not self.enabled or name not in self.sounds:
            return

        if name == "game_over":
            # End-of-round feedback takes priority over any sound still playing.
            for channel in self.channels.values():
                channel.stop()

        channel = self.channels.get(name)
        if channel is not None:
            channel.play(self.sounds[name])

    def stop_all(self):
        for channel in self.channels.values():
            channel.stop()
