import speech_recognition as sr


def listen_for_response():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("Listening for response...")

        audio = recognizer.listen(source)

    try:

        response = recognizer.recognize_google(audio)

        print("You said:", response)

        return response.lower()

    except Exception as e:
        print("Voice error:", e)
        return ""
    







if __name__ == "__main__":

    response = listen_for_response()

    print(response)

