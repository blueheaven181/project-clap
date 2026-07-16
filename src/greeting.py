import asyncio
import edge_tts
import uuid
import os
from playsound import playsound
from datetime import datetime

VOICE = "en-US-GuyNeural"


def get_greeting():

    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good morning Marc"

    elif 12 <= current_hour < 18:
        return "Good afternoon Marc"

    else:
        return "Good evening Marc"




def speak(message):

    filename = f"speech_{uuid.uuid4().hex}.mp3"

    async def generate():
        communicate = edge_tts.Communicate(message, VOICE)
        await communicate.save(filename)

    asyncio.run(generate())

    playsound(filename)
    os.remove(filename)