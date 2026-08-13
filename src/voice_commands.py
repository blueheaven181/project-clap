import time

import speech_recognition as sr
from microphone_config import select_named_microphone

from greeting import speak
from presence_state import set_presence_state


def is_repeated_exact_word(response, expected_word):
    """Accept one or more repetitions of one exact control word."""

    words = response.strip().lower().split()
    return bool(words) and all(word == expected_word for word in words)


def listen_for_response(
    phrase_time_limit=8,
    timeout_seconds=5,
    pause_threshold=0.8,
):
    """Listen until a pause, with a maximum duration for one response."""

    set_presence_state("listening")
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = pause_threshold

    try:
        microphone_index = select_named_microphone(
            sr.Microphone.list_microphone_names()
        )
        with sr.Microphone(device_index=microphone_index) as source:
            print("Adjusting for background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            recognizer.energy_threshold = max(
                recognizer.energy_threshold,
                300,
            )
            recognizer.dynamic_energy_threshold = True

            print(
                "Listening until you finish speaking "
                f"(up to {phrase_time_limit} seconds)..."
            )
            audio = recognizer.listen(
                source,
                timeout=timeout_seconds,
                phrase_time_limit=phrase_time_limit,
            )

        response = recognizer.recognize_google(audio, language="en-US")

        print("You said:", response)
        set_presence_state("thinking")
        return response.lower()

    except sr.WaitTimeoutError:
        print("Voice error: No response was heard.")

    except sr.UnknownValueError:
        print("Voice error: I could not understand the response.")

    except sr.RequestError as error:
        print("Voice service error:", error)

    except Exception as error:
        print("Microphone error:", error)

    set_presence_state("thinking")
    return ""


def listen_until_response(
    retry_message=None,
    timeout_seconds=None,
    silent_retries=False,
    max_attempts=None,
    phrase_time_limit=8,
    pause_threshold=0.8,
):
    """
    Keep listening until CLAP understands a spoken response.

    Return an empty string when the optional timeout or attempt limit expires.
    """

    listening_started = time.monotonic()
    attempts = 0

    while True:
        if (
            timeout_seconds is not None
            and time.monotonic() - listening_started >= timeout_seconds
        ):
            return ""

        if max_attempts is not None and attempts >= max_attempts:
            return ""

        attempts += 1
        response = listen_for_response(
            phrase_time_limit=phrase_time_limit,
            pause_threshold=pause_threshold,
        )

        if response:
            return response

        if (
            timeout_seconds is not None
            and time.monotonic() - listening_started >= timeout_seconds
        ):
            return ""

        can_retry = max_attempts is None or attempts < max_attempts
        if retry_message and not silent_retries and can_retry:
            print(retry_message)
            speak(retry_message)

        time.sleep(0.5)


if __name__ == "__main__":
    response = listen_until_response(
        "I did not hear you. Please try again."
    )
    print("Final response:", response)
