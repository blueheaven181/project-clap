import json
from pathlib import Path
import re

import requests

from greeting import speak
from voice_commands import listen_until_response


OLLAMA_URL = "http://localhost:11434/api/chat"
LOCAL_AI_MODEL = "llama3.2:1b"

SYSTEM_PROMPT = """
You are CLAP, a personal assistant, communication coach,
interview-practice partner, and fitness coach. You are speaking directly to
Marc Anthony Marquez. Always address the person speaking as "you" and "your".
Do not describe the person as a separate person named Marc.

The user is a NOC Engineer based in Abu Dhabi with Azure
Administrator experience.

The user's goals include improving articulation, communication skills,
interview confidence, and ability to express ideas clearly.

Your responses will normally be spoken aloud:
- Use short, natural, voice-friendly sentences.
- Give the direct answer first.
- Keep ordinary answers to a maximum of three short sentences.
- Do not use Markdown, headings, tables, or long lists.
- Ask only one question at a time.
- Give more detail only when the user requests it.
- Never add a personal example unless the user requests one.

When acting as the user's communication and articulation coach:
- Evaluate whether the user's answer is clear, concise, and well structured.
- Point out filler words, repetition, vague language, and long sentences.
- Suggest clearer and more professional wording.
- Provide a stronger version of the answer when useful.
- Give encouraging but honest feedback.
- Focus on only one or two improvements at a time.
- Ask the user to try the improved answer again when appropriate.

When conducting an interview:
- Act as an experienced hiring manager when requested.
- Ask one interview question at a time.
- Wait for the user's answer before continuing.
- Give concise and constructive feedback.
- Evaluate the answer's clarity, relevance, structure, and confidence.
- Suggest a stronger example answer when useful.
- Do not invent facts about the user's professional experience.

When acting as the user's fitness coach:
- Help with general fitness, exercise planning, consistency, and motivation.
- Explain exercises and training concepts in simple language.
- Help estimate calories and macronutrients when enough information is provided.
- Ask about the user's goal, experience, equipment, and limitations before creating a plan.
- Recommend gradual, realistic, and sustainable progress.
- Never diagnose medical conditions.
- Never present calorie or nutrition estimates as exact measurements.
- Recommend professional medical advice for injuries, severe symptoms, or health concerns.
- Keep fitness responses short and practical unless the user requests more detail.

Do not claim to know current live information unless it was
provided by one of CLAP's approved online modules.

Do not pretend to remember information that was not provided in
the current conversation or included in this system prompt.

- Speak directly to the user using "you" and "your", not "Marc" or "he".
"""

def load_marc_profile():
    """
    Load Marc's private local profile without committing it to GitHub.
    """

    project_folder = Path(__file__).resolve().parent.parent
    profile_path = (
        project_folder
        / "config"
        / "marc_profile.local.json"
    )

    try:
        with profile_path.open(
            "r",
            encoding="utf-8",
        ) as profile_file:
            return json.load(profile_file)

    except FileNotFoundError:
        print("Private profile was not found.")
        return {}

    except json.JSONDecodeError as error:
        print("Private profile contains invalid JSON:", error)
        return {}


marc_profile = load_marc_profile()

private_context = (
    SYSTEM_PROMPT
    + "\n\nUse the following facts to personalize your assistance. "
    + "Never mention this profile, private context, JSON, or how these "
    + "facts were stored. "
    + "Your current role is NOC Engineer. Your Azure Administrator, "
    + "system administration, system support, and end-user support "
    + "roles are previous experience. "
    + "Do not change or invent facts about the user's background.\n"
    + "When asked about the user's career, clearly state that they currently "
    + "work as a NOC Engineer and have held this role for more than one "
    + "year. They have more than 15 years of total IT experience. Their "
    + "previous experience includes end-user support, system support, "
    + "system administration, and Azure administration. Never describe "
    + "Azure Administrator as the user's current role.\n"
    + json.dumps(marc_profile, ensure_ascii=False)
)

conversation_history = [
    {
        "role": "system",
        "content": private_context,
    }
]

CONVERSATION_EXIT_PHRASES = {
    "stop",
    "stop talking",
    "stand by",
    "standby",
    "stand bye",
    "stan by",
    "stan bhai",
    "exit",
    "exit conversation",
    "end conversation",
    "goodbye",
    "that is all",
    "that's all",
    "that is enough",
    "that's enough",
    "full stop",
}


def is_conversation_exit_request(message):
    """Recognize exact and naturally repeated conversation exit commands."""

    normalized = " ".join(
        re.findall(r"[a-z']+", message.lower().replace("’", "'"))
    )
    if normalized in CONVERSATION_EXIT_PHRASES:
        return True

    words = normalized.split()
    if "stop" not in words or "not" in words or "don't" in words:
        return False

    stop_fillers = {"stop", "please", "now", "talking", "conversation"}
    return all(word in stop_fillers for word in words)


def use_direct_personal_address(message):
    """Prevent local-model replies from referring to Marc in third person."""

    replacements = (
        (r"\bMarc(?:'s|’s)\b", "your"),
        (r"\bMarc is\b", "you are"),
        (r"\bMarc wants\b", "you want"),
        (r"\bMarc has\b", "you have"),
        (r"\bMarc works\b", "you work"),
    )
    direct_message = message
    for pattern, replacement in replacements:
        direct_message = re.sub(
            pattern,
            replacement,
            direct_message,
            flags=re.IGNORECASE,
        )
    return direct_message

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
                "options": {
                    "num_predict": 80,
                    "temperature": 0.3,
                },
            },
            timeout=120,
        )


        response.raise_for_status()

        assistant_message = use_direct_personal_address(
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

    speak("Conversation mode started.")

    next_message = initial_message
    conversation_turns = 0

    # Temporarily use 2 so the checkpoint is quick to test.
    max_conversation_turns = 10
        # Temporary short values for testing.
    inactivity_timeout_seconds = 120
    presence_timeout_seconds = 30

    while True:
        if next_message:
            user_message = next_message
            next_message = None
        else:
            user_message = listen_until_response(
                timeout_seconds=inactivity_timeout_seconds,
                silent_retries=True,
            )

            if not user_message:
                speak("Marc, are you still there?")

                presence_response = listen_until_response(
                    timeout_seconds=presence_timeout_seconds,
                    silent_retries=True,
                )

                if not presence_response:
                    speak(
                        "I did not hear a response. "
                        "I am returning to standby."
                    )
                    return

                presence_words = {
                    "yes",
                    "yeah",
                    "yep",
                    "here",
                    "i am here",
                    "still here",
                }

                if any(
                    phrase in presence_response
                    for phrase in presence_words
                ):
                    speak(
                        "Welcome back. Would you like to continue "
                        "where we left off, or start a new topic?"
                    )
                    continue

                speak("Okay Marc, standing by.")
                return

        normalized_message = user_message.strip().lower()

        if is_conversation_exit_request(normalized_message):
            speak("Conversation mode ended. Standing by.")
            return

        print("Marc:", user_message)

        assistant_message = chat_with_clap(user_message)

        print("CLAP:", assistant_message)
        speak(assistant_message)

        conversation_turns += 1

        if conversation_turns >= max_conversation_turns:
            speak(
                "Would you like to continue our conversation?"
            )

            continue_response = listen_until_response(
                "I did not hear you. Please say yes or no."
            )

            continue_words = {
                "yes",
                "yeah",
                "yep",
                "sure",
                "continue",
                "okay",
                "ok",
            }

            if any(
                word in continue_response.split()
                for word in continue_words
            ):
                conversation_turns = 0
                speak("Okay, let us continue.")
            else:
                speak("Conversation mode ended. Standing by.")
                return



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
