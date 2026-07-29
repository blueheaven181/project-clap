import asyncio
import edge_tts
import uuid
from playsound import playsound
from datetime import datetime
from pathlib import Path

VOICE = "en-US-GuyNeural"

PROJECT_FOLDER = Path(__file__).resolve().parent.parent


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


def get_greeting():

    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good morning Marc"

    elif 12 <= current_hour < 18:
        return "Good afternoon Marc"

    else:
        return "Good evening Marc"




def speak(message):
    filename = (
        PROJECT_FOLDER
        / f"speech_{uuid.uuid4().hex}.mp3"
    )

    async def generate():
        communicate = edge_tts.Communicate(
            message,
            VOICE,
            rate="+8%",
        )
        await communicate.save(str(filename))

    try:
        asyncio.run(generate())
        playsound(str(filename))

    finally:
        try:
            filename.unlink(missing_ok=True)
        except OSError as error:
            print(
                "Temporary speech file will be removed "
                "when CLAP starts again:",
                error,
            )