import time
import sys
import subprocess

import speech_recognition as sr
import requests
from speech_recognition.recognizers.google import (
    ENDPOINT,
    OutputParser,
    create_request_builder,
)
from speech_recognition.audio import get_flac_converter
from microphone_config import select_named_microphone

from greeting import speak
from presence_state import set_presence_state
from wake_audio_session import capture_command_audio, suspend_wake_stream


def is_repeated_exact_word(response, expected_word):
    """Accept one or more repetitions of one exact control word."""

    words = response.strip().lower().split()
    return bool(words) and all(word == expected_word for word in words)


def close_microphone_safely(microphone):
    """Close PyAudio without discarding audio on a late Windows driver error."""

    try:
        microphone.__exit__(None, None, None)
        return True
    except Exception as error:
        print("Command microphone close warning:", error, flush=True)
        return False


def recognize_google_packaged(audio, language="en-US"):
    """Recognize speech without Windows proxy discovery in frozen builds."""

    builder = create_request_builder(endpoint=ENDPOINT, language=language)
    wav_data = audio.get_wav_data(convert_width=2)
    process = subprocess.Popen(
        [get_flac_converter(), "--stdout", "--totally-silent", "--best", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    flac_data, _ = process.communicate(wav_data)
    if process.returncode:
        raise sr.RequestError("Packaged audio conversion failed.")
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.post(
            builder.build_url(),
            data=flac_data,
            headers={"Content-Type": f"audio/x-flac; rate={audio.sample_rate}"},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise sr.RequestError(str(error)) from error
    return OutputParser(show_all=False, with_confidence=False).parse(response.text)


def listen_for_response(
    phrase_time_limit=8,
    timeout_seconds=5,
    pause_threshold=0.8,
):
    """Listen until a pause, with a maximum duration for one response."""

    set_presence_state("listening")
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = pause_threshold

    stage = "initialization"
    try:
        if getattr(sys, "frozen", False):
            stage = "shared-stream capture"
            print("Command microphone selected: shared Fifine wake stream", flush=True)
            print("Adjusting for background noise...")
            print(
                "Listening until you finish speaking "
                f"(up to {phrase_time_limit} seconds)..."
            )
            try:
                pcm = capture_command_audio(
                    timeout_seconds=timeout_seconds,
                    phrase_time_limit=phrase_time_limit,
                    pause_threshold=pause_threshold,
                )
            except TimeoutError as error:
                raise sr.WaitTimeoutError(str(error)) from error
            stage = "audio preparation"
            audio = sr.AudioData(pcm, sample_rate=16000, sample_width=2)
        else:
        # PyAudio and the wake-word backend cannot reliably share the same
        # packaged Windows input stream. Pause wake detection only while this
        # command-listening turn owns the preferred microphone. Resolve by
        # name each time because packaged PyAudio's default can differ from
        # the Windows/sounddevice default.
            with suspend_wake_stream():
                microphone_names = sr.Microphone.list_microphone_names()
                microphone_index = select_named_microphone(microphone_names)
                if microphone_index is None:
                    print("Command microphone selected: Windows default", flush=True)
                else:
                    print(
                        "Command microphone selected:",
                        microphone_names[microphone_index],
                        flush=True,
                    )
                microphone = sr.Microphone(device_index=microphone_index)
                source = microphone.__enter__()
                try:
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
                finally:
                    close_microphone_safely(microphone)

        stage = "speech recognition"
        if getattr(sys, "frozen", False):
            response = recognize_google_packaged(audio, language="en-US")
        else:
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
        print(f"Voice pipeline error during {stage}:", error, flush=True)

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
