import speech_recognition as sr
import time

from greeting import speak
    
def listen_for_response():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone(device_index=1) as source:
            print("Adjusting for background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            recognizer.energy_threshold = max(
            recognizer.energy_threshold,
              1000
            )
            recognizer.dynamic_energy_threshold = False


            print("Listening for 5 seconds — speak now....")
            audio = recognizer.record(source, duration=5)
            

        response = recognizer.recognize_google(audio, language="en-US")

        print("You said:", response)
        return response.lower()

    except sr.WaitTimeoutError:
        print("Voice error: No response was heard.")

    except sr.UnknownValueError:
        print("Voice error: I could not understand the response.")

    except sr.RequestError as error:
        print("Voice service error:", error)

    except Exception as error:
        print("Microphone error:", error)

    return ""


def listen_until_response(
    retry_message=None,
    timeout_seconds=None,
    silent_retries=False,
):
    """
    Keep listening until CLAP understands a spoken response.

    Return an empty string when the optional timeout expires.
    """

    listening_started = time.monotonic()

    while True:
        if (
            timeout_seconds is not None
            and time.monotonic() - listening_started
            >= timeout_seconds
        ):
            return ""

        response = listen_for_response()

        if response:
            return response

        if (
            timeout_seconds is not None
            and time.monotonic() - listening_started
            >= timeout_seconds
        ):
            return ""

        if retry_message and not silent_retries:
            print(retry_message)
            speak(retry_message)

        time.sleep(0.5)


if __name__ == "__main__":

    response = listen_until_response(
        "I did not hear you, Please try again."
    )
    print("Final response:", response)

