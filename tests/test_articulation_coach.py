import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import articulation_coach
import command_router


class ArticulationIntentTests(unittest.TestCase):
    def test_articulation_training_request_is_recognized(self):
        self.assertTrue(
            articulation_coach.is_articulation_training_request(
                "start articulation training"
            )
        )

    def test_unrelated_practice_is_not_recognized(self):
        self.assertFalse(
            articulation_coach.is_articulation_training_request(
                "practice guitar"
            )
        )

    def test_communication_coaching_is_recognized(self):
        self.assertTrue(
            articulation_coach.is_articulation_training_request(
                "start communication coaching"
            )
        )

    def test_common_voice_recognition_variant_is_recognized(self):
        self.assertTrue(
            articulation_coach.is_articulation_training_request(
                "start article asian trading"
            )
        )

    def test_mode_is_selected_from_spoken_command(self):
        mode = articulation_coach.get_requested_exercise_mode(
            "practice a technical explanation"
        )

        self.assertEqual("technical_explanation", mode)

    def test_filler_words_are_counted_from_transcript(self):
        count = articulation_coach.count_filler_words(
            "Um, I basically fixed it, you know."
        )

        self.assertEqual(3, count)

    def test_feedback_prompt_contains_the_spoken_answer(self):
        prompt = articulation_coach.build_feedback_prompt(
            "I resolved the network alert and updated the ticket."
        )

        self.assertIn("resolved the network alert", prompt)
        self.assertIn("one strength", prompt)
        self.assertIn("single most important improvement", prompt)
        for category in {
            "clarity", "conciseness", "structure", "filler words", "confidence"
        }:
            self.assertIn(category, prompt)
        self.assertIn("Do not assume or invent", prompt)

    def test_feedback_prompt_marks_confidence_as_transcript_based(self):
        prompt = articulation_coach.build_feedback_prompt("I completed the task.")

        self.assertIn("transcript-based", prompt)
        self.assertIn("do not claim to assess vocal tone", prompt)


class ArticulationRoutingTests(unittest.TestCase):
    @patch(
        "command_router.start_articulation_training",
        return_value=True,
    )
    def test_articulation_command_starts_training(self, start_training):
        recognized = command_router.route_command(
            "start articulation training"
        )

        self.assertTrue(recognized)
        start_training.assert_called_once_with()

    @patch(
        "command_router.start_articulation_training",
        return_value=True,
    )
    def test_articulation_mode_routes_to_selected_exercise(self, start_training):
        recognized = command_router.route_command(
            "practice a technical explanation"
        )

        self.assertTrue(recognized)
        start_training.assert_called_once_with(
            exercise_mode="technical_explanation"
        )


class ArticulationSessionTests(unittest.TestCase):
    def test_original_numeric_exercise_selection_is_preserved(self):
        selected_mode = articulation_coach.resolve_exercise_mode(
            exercise_index=1
        )

        self.assertEqual("technical_explanation", selected_mode)

    @patch("articulation_coach.speak")
    @patch(
        "articulation_coach.evaluate_articulation_answer",
        return_value="Clear structure. Shorten the second sentence.",
    )
    @patch(
        "articulation_coach.listen_until_response",
        side_effect=["My first answer", "no"],
    )
    def test_session_gives_feedback_without_forcing_retry(
        self,
        listen_mock,
        evaluate,
        _speak,
    ):
        completed = articulation_coach.start_articulation_training()

        self.assertTrue(completed)
        evaluate.assert_called_once_with("My first answer")
        first_listen = listen_mock.call_args_list[0]
        self.assertEqual(45, first_listen.kwargs["phrase_time_limit"])
        self.assertEqual(1.5, first_listen.kwargs["pause_threshold"])

    @patch("articulation_coach.speak")
    @patch("articulation_coach.evaluate_articulation_answer")
    @patch(
        "articulation_coach.listen_until_response",
        return_value="stop",
    )
    def test_stop_cancels_without_scoring(
        self,
        _listen,
        evaluate,
        speak_mock,
    ):
        completed = articulation_coach.start_articulation_training()

        self.assertTrue(completed)
        evaluate.assert_not_called()
        speak_mock.assert_called_with(
            "Articulation training cancelled. Returning to standby."
        )

    @patch("articulation_coach.speak")
    @patch(
        "articulation_coach.evaluate_articulation_answer",
        return_value="Scored feedback.",
    )
    @patch(
        "articulation_coach.listen_until_response",
        side_effect=["My answer", ""],
    )
    def test_missing_retry_decision_ends_session(
        self,
        _listen,
        evaluate,
        speak_mock,
    ):
        completed = articulation_coach.start_articulation_training()

        self.assertTrue(completed)
        evaluate.assert_called_once_with("My answer")
        speak_mock.assert_called_with(
            "Articulation training complete. Returning to standby."
        )

    @patch("articulation_coach.speak")
    @patch(
        "articulation_coach.evaluate_articulation_answer",
        return_value="Scored feedback.",
    )
    @patch(
        "articulation_coach.listen_until_response",
        side_effect=["My technical answer", "no"],
    )
    def test_session_uses_selected_exercise_mode(
        self,
        _listen,
        _evaluate,
        speak_mock,
    ):
        articulation_coach.start_articulation_training(
            exercise_mode="technical_explanation"
        )

        spoken_messages = [call.args[0] for call in speak_mock.call_args_list]
        self.assertTrue(
            any("technical explanation mode" in message for message in spoken_messages)
        )
        self.assertIn(
            articulation_coach.EXERCISE_MODES["technical_explanation"]["prompt"],
            spoken_messages,
        )


if __name__ == "__main__":
    unittest.main()
