import threading

import speech_recognition as sr

from greeting import speak, stop_speaking


MICROPHONE_INDEX = 1

STOP_PHRASES = {
    "stop",
    "clap stop",
    "clap staff",
    "club stop",
    "club staff",
    "hey clap stop",
    "hey club stop",
    "full stop",
}
    



def normalize_phrase(phrase):
    """
    Normalize a recognized phrase for command comparison.
    """

    return phrase.strip().lower().replace(",", "").replace(".", "")


def run_voice_interrupt_test():
    recognizer = sr.Recognizer()

    message = (
        "Marc, this is a test of my global interruption system. "
        "I will keep speaking for several sentences while the "
        "microphone listens independently. "
        "You may interrupt this message at any moment. "
        "The assistant should hear your instruction and immediately "
        "end the current spoken response. "
        "This experiment helps us confirm that playback and microphone "
        "recognition can operate at the same time."
    )

    with sr.Microphone(
        device_index=MICROPHONE_INDEX
    ) as source:
        print("Adjusting microphone before speech starts...")
        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5,
        )

        recognizer.energy_threshold = max(
            recognizer.energy_threshold,
            1000,
        )
        recognizer.dynamic_energy_threshold = False

        speech_worker = threading.Thread(
            target=speak,
            args=(message,),
        )
        speech_worker.start()

        print('Say "CLAP stop" while CLAP is speaking.')

        while speech_worker.is_alive():
            try:
                audio = recognizer.listen(
                    source,
                    timeout=1,
                    phrase_time_limit=2,
                )

            except sr.WaitTimeoutError:
                continue

            try:
                heard_phrase = recognizer.recognize_google(
                    audio,
                    language="en-US",
                )

            except sr.UnknownValueError:
                continue

            except sr.RequestError as error:
                print("Voice service error:", error)
                break

            normalized_phrase = normalize_phrase(
                heard_phrase
            )

            print("Interrupt listener heard:", normalized_phrase)

            if normalized_phrase in STOP_PHRASES:
                print("GLOBAL STOP DETECTED")
                stop_speaking()
                break

        speech_worker.join()

    print("Voice-interruption test completed.")


if __name__ == "__main__":
    try:
        run_voice_interrupt_test()

    except KeyboardInterrupt:
        stop_speaking()
        print("\nVoice-interruption test stopped.")