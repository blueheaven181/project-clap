import speech_recognition as sr
import time

    
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


if __name__ == "__main__":

    response = listen_for_response()

    print(response)

