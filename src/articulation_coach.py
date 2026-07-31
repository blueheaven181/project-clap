from conversation import chat_with_clap
from greeting import speak
from voice_commands import listen_until_response


ARTICULATION_PROMPTS = (
    (
        "Give a short work update. Explain what you completed, "
        "what problem you faced, and what you will do next."
    ),
    (
        "Explain a technical issue to a non-technical colleague. "
        "State the problem, its impact, and the next action."
    ),
    (
        "Describe one professional achievement. Explain the situation, "
        "your action, and the result."
    ),
)


def is_articulation_training_request(command):
    """Return True when a transcript asks for articulation practice."""

    normalized_command = command.strip().lower()

    phrases = {
        "articulation training",
        "articulation practice",
        "communication training",
        "communication practice",
        "communication coaching",
        "speaking practice",
        "speaking coach",
        "help me with speaking",
        "practice my speaking",
        "articulation coach",
        "improve my articulation",
        "train my communication",
    }

    return any(phrase in normalized_command for phrase in phrases)


def build_feedback_prompt(answer):
    """Create a consistent, voice-friendly coaching request."""

    return (
        "Act as my articulation coach. Evaluate this spoken answer: "
        f'"{answer}". '
        "Respond in four short spoken parts. First, name one strength. "
        "Second, name the single most important improvement. Third, give "
        "a clearer version using only facts from my answer. Fourth, end with "
        "one short encouragement. Do not use Markdown."
    )


def evaluate_articulation_answer(answer):
    """Request concise articulation feedback from the local AI."""

    return chat_with_clap(build_feedback_prompt(answer))


def start_articulation_training(exercise_index=0):
    """Run one guided articulation exercise with an optional retry."""

    prompt = ARTICULATION_PROMPTS[
        exercise_index % len(ARTICULATION_PROMPTS)
    ]

    speak(
        "Articulation training started. Focus on short sentences, "
        "a clear structure, and one main idea at a time."
    )
    speak(prompt)

    answer = listen_until_response(
        "I did not hear your answer. Please try again."
    )

    print("Articulation answer:", answer)

    feedback = evaluate_articulation_answer(answer)
    print("Articulation feedback:", feedback)
    speak(feedback)

    speak("Would you like to try the answer one more time?")
    retry_response = listen_until_response(
        "I did not hear you. Please say yes or no."
    )

    yes_words = {
        "yes",
        "yeah",
        "yep",
        "sure",
        "okay",
        "ok",
        "retry",
        "again",
    }

    if any(word in retry_response.lower().split() for word in yes_words):
        speak("Go ahead. Give your improved answer now.")
        improved_answer = listen_until_response(
            "I did not hear your improved answer. Please try again."
        )

        improved_feedback = evaluate_articulation_answer(improved_answer)
        print("Improved articulation feedback:", improved_feedback)
        speak(improved_feedback)

    speak("Articulation training complete. Returning to standby.")
    return True
