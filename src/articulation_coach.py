import re

from conversation import chat_with_clap
from greeting import speak
from voice_commands import listen_until_response


EXERCISE_MODES = {
    "work_update": {
        "name": "work update",
        "prompt": (
            "Give a short work update. Explain what you completed, "
            "what problem you faced, and what you will do next."
        ),
        "keywords": {"work update", "status update", "project update"},
    },
    "technical_explanation": {
        "name": "technical explanation",
        "prompt": (
            "Explain a technical issue to a non-technical colleague. "
            "State the problem, its impact, and the next action."
        ),
        "keywords": {
            "technical explanation",
            "explain a technical issue",
            "technical issue",
        },
    },
    "achievement": {
        "name": "achievement story",
        "prompt": (
            "Describe one professional achievement. Explain the situation, "
            "your action, and the result."
        ),
        "keywords": {
            "achievement",
            "achievement story",
            "situation action result",
            "star answer",
        },
    },
}

# Kept as a tuple for callers that used the original prompt collection.
ARTICULATION_PROMPTS = tuple(
    mode["prompt"] for mode in EXERCISE_MODES.values()
)

FILLER_PATTERNS = (
    r"\bum+\b",
    r"\buh+\b",
    r"\berm+\b",
    r"\byou know\b",
    r"\bi mean\b",
    r"\bbasically\b",
    r"\bactually\b",
    r"\blike\b",
)


def normalize_voice_command(command):
    """Normalize punctuation and common articulation recognition variants."""

    normalized = re.sub(r"[^a-z0-9\s]", " ", command.strip().lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()

    recognition_variants = {
        "article asian": "articulation",
        "articulation trading": "articulation training",
        "communication train": "communication training",
        "speaking practise": "speaking practice",
    }

    for variant, replacement in recognition_variants.items():
        normalized = normalized.replace(variant, replacement)

    return normalized


def is_articulation_training_request(command):
    """Return True when a transcript asks for articulation practice."""

    normalized_command = normalize_voice_command(command)

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
        "practice a work update",
        "practice a technical explanation",
        "practice an achievement story",
    }

    return any(phrase in normalized_command for phrase in phrases)


def get_requested_exercise_mode(command):
    """Return the exercise mode requested in a spoken command, if present."""

    normalized_command = normalize_voice_command(command)

    for mode_key, mode in EXERCISE_MODES.items():
        if any(
            keyword in normalized_command
            for keyword in mode["keywords"]
        ):
            return mode_key

    return None


def count_filler_words(answer):
    """Count common spoken fillers found in the recognized transcript."""

    normalized_answer = answer.lower()
    return sum(
        len(re.findall(pattern, normalized_answer))
        for pattern in FILLER_PATTERNS
    )


def build_feedback_prompt(answer):
    """Create a consistent, voice-friendly scored coaching request."""

    filler_count = count_filler_words(answer)

    return (
        "Act as my articulation coach. Evaluate only this spoken transcript: "
        f'"{answer}". '
        "Do not assume or invent personal, career, technical, or outcome facts. "
        "Give integer scores from 1 to 5 for clarity, conciseness, structure, "
        "filler words, and confidence. A higher score is always better. "
        "Use 1 for needs substantial work, 3 for effective with room to improve, "
        "and 5 for consistently strong. "
        "For filler words, use the transcript count supplied here: "
        f"{filler_count}; score 5 for zero, 4 for one, 3 for two, 2 for three "
        "or four, and 1 for five or more. For confidence, judge only the wording "
        "for directness and unnecessary qualifiers, and label the "
        "score as transcript-based; do not claim to assess vocal tone. "
        "Respond with a short scorecard containing the five labeled scores. "
        "Then give one strength, the single most important improvement, a clearer "
        "version using only facts from the answer, and one short encouragement. "
        "Do not use Markdown."
    )


def evaluate_articulation_answer(answer):
    """Request concise articulation feedback from the local AI."""

    return chat_with_clap(build_feedback_prompt(answer))


def resolve_exercise_mode(exercise_mode=None, exercise_index=None):
    """Resolve a named mode while supporting the original numeric argument."""

    if exercise_mode in EXERCISE_MODES:
        return exercise_mode

    mode_keys = tuple(EXERCISE_MODES)
    if exercise_index is not None:
        return mode_keys[exercise_index % len(mode_keys)]

    return "work_update"


def start_articulation_training(exercise_index=0, exercise_mode=None):
    """Run one guided articulation exercise with an optional retry."""

    selected_mode = resolve_exercise_mode(exercise_mode, exercise_index)
    mode = EXERCISE_MODES[selected_mode]

    speak(
        f"Articulation training started in {mode['name']} mode. "
        "Focus on short sentences, a clear structure, and one main idea "
        "at a time."
    )
    speak(mode["prompt"])

    answer = listen_until_response(
        "I did not hear your answer. Please try again."
    )

    print("Articulation answer received for scoring.")

    feedback = evaluate_articulation_answer(answer)
    print("Articulation feedback:", feedback)
    speak(feedback)

    speak("Would you like to try the answer one more time?")
    retry_response = listen_until_response(
        "I did not hear you. Please say yes or no."
    )

    yes_words = {
        "yes", "yeah", "yep", "sure", "okay", "ok", "retry", "again",
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
