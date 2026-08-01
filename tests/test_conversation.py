import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import conversation
from conversation import (
    is_conversation_exit_request,
    use_direct_personal_address,
)


class PersonalAddressTests(unittest.TestCase):
    def test_marc_is_addressed_as_the_user(self):
        response = (
            "You want to improve Marc's articulation. "
            "Marc is a NOC Engineer and Marc has extensive experience."
        )

        self.assertEqual(
            use_direct_personal_address(response),
            "You want to improve your articulation. "
            "you are a NOC Engineer and you have extensive experience.",
        )


class ConversationExitTests(unittest.TestCase):
    def test_natural_and_repeated_stop_phrases_are_recognized(self):
        for phrase in (
            "stop now",
            "stop stop stop stop",
            "please stop now",
            "stop talking now",
            "end conversation",
        ):
            with self.subTest(phrase=phrase):
                self.assertTrue(is_conversation_exit_request(phrase))

    def test_unrelated_use_of_stop_is_not_an_exit(self):
        self.assertFalse(
            is_conversation_exit_request("how can I stop procrastinating")
        )
        self.assertFalse(is_conversation_exit_request("do not stop"))

    @patch("conversation.chat_with_clap")
    @patch("conversation.speak")
    def test_stop_now_exits_without_calling_local_ai(self, speak, chat):
        conversation.start_voice_conversation(initial_message="stop now")

        chat.assert_not_called()
        speak.assert_any_call("Conversation mode ended. Standing by.")


if __name__ == "__main__":
    unittest.main()
