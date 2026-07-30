import asyncio
import uuid
from pathlib import Path

import edge_tts
import pygame


VOICE = "en-US-GuyNeural"
PROJECT_FOLDER = Path(__file__).resolve().parent.parent
SPEECH_CHANNEL_NUMBER = 1


def generate_test_speech(filename):
    """
    Generate a sufficiently long message for playback testing.
    """

    message = (
        "This is CLAP testing the new controllable speech system. "
        "The purpose of this test is to confirm that my voice can "
        "be paused, continued, and stopped without affecting other "
        "parts of the assistant. "
        "When requested, I should immediately pause speaking. "
        "When requested again, I should continue from where I stopped. "
        "Finally, the stop command should end this message completely."
    )

    async def generate():
        communicate = edge_tts.Communicate(
            message,
            VOICE,
            rate="+8%",
        )
        await communicate.save(str(filename))

    asyncio.run(generate())


def run_test():
    filename = (
        PROJECT_FOLDER
        / f"speech_test_{uuid.uuid4().hex}.mp3"
    )

    try:
        generate_test_speech(filename)

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        speech_sound = pygame.mixer.Sound(str(filename))
        speech_channel = pygame.mixer.Channel(
            SPEECH_CHANNEL_NUMBER
        )

        speech_channel.play(speech_sound)

        input("Press Enter to PAUSE CLAP's voice...")
        speech_channel.pause()

        input("Press Enter to CONTINUE CLAP's voice...")
        speech_channel.unpause()

        input("Press Enter to STOP CLAP's voice...")
        speech_channel.stop()

        print("Speech-control test completed.")

    finally:
        try:
            filename.unlink(missing_ok=True)
        except OSError as error:
            print("Could not remove test speech file:", error)


if __name__ == "__main__":
    run_test()