import asyncio
import edge_tts
from playsound import playsound

VOICE = "en-US-GuyNeural"


def speak(message):
    async def generate():
        communicate = edge_tts.Communicate(message, VOICE)
        await communicate.save("speech.mp3")

    asyncio.run(generate())
    playsound("speech.mp3")