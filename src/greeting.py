import asyncio
import threading
import uuid
from datetime import datetime
from pathlib import Path

import edge_tts
import pygame


VOICE = "en-US-GuyNeural"
SPEECH_CHANNEL_NUMBER = 1
SPEECH_VOLUME = 1.0

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

_speech_channel = None
_last_spoken_message = ""
_speech_paused = False
_speech_stopped = False

_speech_control_event = threading.Event()
_speech_control_handler = None


def cleanup_old_speech_files():
    """
    Remove temporary speech files left by interrupted CLAP sessions.
    """

    for speech_file in PROJECT_FOLDER.glob("speech_*.mp3"):
        try:
            speech_file.unlink()
        except OSError as error:
            print("Could not remove old speech file:", error)


cleanup_old_speech_files()


def get_speech_channel():
    """
    Return CLAP's dedicated pygame speech channel.
    """

    global _speech_channel

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    if _speech_channel is None:
        _speech_channel = pygame.mixer.Channel(
            SPEECH_CHANNEL_NUMBER
        )
        _speech_channel.set_volume(SPEECH_VOLUME)

    return _speech_channel


def get_greeting():
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good morning Marc"

    if 12 <= current_hour < 18:
        return "Good afternoon Marc"

    return "Good evening Marc"


def is_speaking():
    """
    Return True while CLAP is speaking or paused.
    """

    channel_is_busy = (
        _speech_channel is not None
        and _speech_channel.get_busy()
    )

    return channel_is_busy or _speech_paused


def set_speech_control_handler(handler):
    """
    Register the function that asks Marc for a speech-control command.
    """

    global _speech_control_handler

    _speech_control_handler = handler


def request_speech_control(trigger):
    """
    Pause CLAP only for a verified physical double-clap trigger.
    """

    if trigger != "double_clap":
        return False

    if _speech_control_event.is_set() or _speech_paused:
        return False

    if not is_speaking():
        return False

    _pause_speaking()
    _speech_control_event.set()

    return True


def stop_speaking():
    """
    Stop CLAP's current spoken message.
    """

    global _speech_paused
    global _speech_stopped

    _speech_paused = False
    _speech_stopped = True

    speech_channel = get_speech_channel()
    speech_channel.stop()


def _pause_speaking():
    """
    Pause CLAP's current spoken message after trigger validation.
    """

    global _speech_paused

    _speech_paused = True

    speech_channel = get_speech_channel()
    speech_channel.pause()


def resume_speaking():
    """
    Continue CLAP's paused spoken message.
    """

    global _speech_paused

    speech_channel = get_speech_channel()
    speech_channel.unpause()

    _speech_paused = False


def repeat_last_speech():
    """
    Repeat CLAP's most recent spoken message.
    """

    if not _last_spoken_message:
        return False

    speak(_last_spoken_message)
    return True


def speak(message):
    """
    Generate and play controllable CLAP speech.
    """

    global _last_spoken_message
    global _speech_paused
    global _speech_stopped

    _last_spoken_message = str(message)

    filename = (
        PROJECT_FOLDER
        / f"speech_{uuid.uuid4().hex}.mp3"
    )

    async def generate():
        communicate = edge_tts.Communicate(
            _last_spoken_message,
            VOICE,
            rate="+8%",
        )
        await communicate.save(str(filename))

    try:
        asyncio.run(generate())

        speech_channel = get_speech_channel()
        speech_sound = pygame.mixer.Sound(str(filename))

        speech_channel.stop()

        _speech_paused = False
        _speech_stopped = False
        _speech_control_event.clear()

        speech_channel.play(speech_sound)

        while True:
            if _speech_stopped:
                break

            if _speech_control_event.is_set():
                _speech_control_event.clear()

                if _speech_control_handler is None:
                    action = "stop"
                else:
                    action = _speech_control_handler()

                normalized_action = (
                    str(action).strip().lower()
                )

                if normalized_action == "continue":
                    resume_speaking()

                elif normalized_action == "repeat":
                    _speech_paused = False
                    _speech_stopped = False

                    speech_channel.stop()
                    speech_channel.play(speech_sound)

                else:
                    stop_speaking()
                    break

                continue

            if _speech_paused:
                pygame.time.wait(50)
                continue

            if not speech_channel.get_busy():
                break

            pygame.time.wait(50)

    finally:
        _speech_paused = False
        _speech_control_event.clear()

        try:
            filename.unlink(missing_ok=True)
        except OSError as error:
            print(
                "Temporary speech file will be removed "
                "when CLAP starts again:",
                error,
            )

    return not _speech_stopped
