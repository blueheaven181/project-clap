from pathlib import Path

import pygame


MUSIC_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "briefing_music.mp3"
)


def start_background_music(volume=0.15):
    if not MUSIC_PATH.exists():
        raise FileNotFoundError(
            f"Background music not found: {MUSIC_PATH}"
        )

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    pygame.mixer.music.load(str(MUSIC_PATH))
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loops=-1)

    print("Background music started.")


def stop_background_music():
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(1000)
        print("Background music stopped.")


if __name__ == "__main__":
    try:
        start_background_music()
        input("Press Enter to stop the music...")
    finally:
        stop_background_music()