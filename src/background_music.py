from pathlib import Path

import pygame
from runtime_paths import data_path


MUSIC_PATH = data_path("assets", "briefing_music.mp3")

_background_music_paused = False


def start_background_music(volume=0.15):
    global _background_music_paused

    if not MUSIC_PATH.exists():
        raise FileNotFoundError(
            f"Background music not found: {MUSIC_PATH}"
        )

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    pygame.mixer.music.load(str(MUSIC_PATH))
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loops=-1)

    _background_music_paused = False
    print("Background music started.")


def pause_background_music():
    """
    Pause the briefing music if it is currently playing.
    """

    global _background_music_paused

    if (
        pygame.mixer.get_init()
        and pygame.mixer.music.get_busy()
        and not _background_music_paused
    ):
        pygame.mixer.music.pause()
        _background_music_paused = True
        print("Background music paused.")


def resume_background_music():
    """
    Resume briefing music that CLAP previously paused.
    """

    global _background_music_paused

    if pygame.mixer.get_init() and _background_music_paused:
        pygame.mixer.music.unpause()
        _background_music_paused = False
        print("Background music resumed.")


def stop_background_music():
    global _background_music_paused

    if pygame.mixer.get_init():
        pygame.mixer.music.fadeout(1000)

        if (
            pygame.mixer.music.get_busy()
            or _background_music_paused
        ):
            print("Background music stopped.")

    _background_music_paused = False


if __name__ == "__main__":
    try:
        start_background_music()
        input("Press Enter to stop the music...")
    finally:
        stop_background_music()
