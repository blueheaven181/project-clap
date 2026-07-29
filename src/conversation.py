import requests

from greeting import speak
from voice_commands import listen_until_response


OLLAMA_URL = "http://localhost:11434/api/chat"
LOCAL_AI_MODEL = "llama3.2:1b"

SYSTEM_PROMPT = """
You are CLAP, Marc Anthony Marquez's personal assistant,
communication coach, and interview-practice partner.

Marc is a NOC Engineer based in Abu Dhabi with Azure
Administrator experience. Explain concepts clearly and
help him improve his confidence and professional communication.

When conducting an interview:
- Ask one question at a time.
- Wait for Marc's answer.
- Give concise and constructive feedback.
- Suggest a stronger example answer when useful.

Do not claim to know current live information unless it was
provided by one of CLAP's approved online modules.
"""

conversation_history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }
]


def chat_with_clap(user_message):
    conversation_history.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": LOCAL_AI_MODEL,
                "messages": conversation_history,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        assistant_message = (
            response.json()["message"]["content"].strip()
        )

        conversation_history.append(
            {
                "role": "assistant",
                "content": assistant_message,
            }
        )

        return assistant_message

    except requests.RequestException as error:
        print("Local AI connection error:", error)

        return (
            "I cannot connect to my local AI engine right now. "
            "Please make sure Ollama is running."
        )


def start_voice_conversation(initial_message=None):
    """
    Start a hands-free conversation with CLAP's local AI.
    """

    exit_phrases = {
        "stop",
        "exit",
        "goodbye",
        "that is all",
        "that's all",
        "stop conversation",
    }

    speak("Conversation mode started.")

    next_message = initial_message

    while True:
        if next_message:
            user_message = next_message
            next_message = None
        else:
            user_message = listen_until_response(
                "I did not hear you. Please say that again."
            )

        if user_message.strip() in exit_phrases:
            speak("Conversation mode ended. Standing by.")
            return

        print("Marc:", user_message)

        assistant_message = chat_with_clap(user_message)

        print("CLAP:", assistant_message)
        speak(assistant_message)



if __name__ == "__main__":
    print("CLAP local conversation test")
    print("Type 'exit' to stop.")

    while True:
        user_message = input("\nMarc: ").strip()

        if user_message.lower() in {"exit", "quit"}:
            print("CLAP: Conversation ended.")
            break

        if not user_message:
            continue

        response = chat_with_clap(user_message)

        print("\nCLAP:", response)