import asyncio
import edge_tts
from playsound import playsound

TEXT = "Good evening Marc. Project CLAP has been activated. System health is green. No critical alerts detected. Azure resources are operational. Weather in Abu Dhabi is thirty nine degrees. Shall I begin your morning playlist? "

VOICE = "en-US-GuyNeural"

OUTPUT_FILE = "greeting.mp3"

async def main():
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)

asyncio.run(main())

playsound(OUTPUT_FILE)