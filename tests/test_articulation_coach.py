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

    def test_feedback_prompt_contains_the_spoken_answer(self):
        prompt = articulation_coach.build_feedback_prompt(
            "I resolved the network alert and updated the ticket."
        )

        self.assertIn("resolved the network alert", prompt)
        self.assertIn("one strength", prompt)
        self.assertIn("single most important improvement", prompt)


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


class ArticulationSessionTests(unittest.TestCase):
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
        _listen,
        evaluate,
        _speak,
    ):
        completed = articulation_coach.start_articulation_training()

        self.assertTrue(completed)
        evaluate.assert_called_once_with("My first answer")


if __name__ == "__main__":
    unittest.main()
