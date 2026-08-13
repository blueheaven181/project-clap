import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import conversation
import conversation_voice
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
            "stop now full stop",
            "full stop full stop",
            "please end conversation stop now",
            "end conversation",
        ):
            with self.subTest(phrase=phrase):
                self.assertTrue(is_conversation_exit_request(phrase))

    def test_unrelated_use_of_stop_is_not_an_exit(self):
        self.assertFalse(
            is_conversation_exit_request("how can I stop procrastinating")
        )
        self.assertFalse(is_conversation_exit_request("do not stop"))
        self.assertFalse(is_conversation_exit_request("stop the music"))

    @patch("conversation.chat_with_clap")
    @patch("conversation.speak")
    def test_stop_now_exits_without_calling_local_ai(self, speak, chat):
        conversation.start_voice_conversation(initial_message="stop now")

        chat.assert_not_called()
        speak.assert_any_call("Conversation mode ended. Standing by.")

    @patch("conversation.listen_until_response")
    @patch("conversation.respond_in_conversation", return_value="Answer")
    @patch("conversation.speak")
    def test_stop_at_turn_limit_takes_precedence_over_ai(
        self,
        speak,
        respond,
        listen,
    ):
        listen.return_value = "stop now full stop"

        with patch.object(conversation, "respond_in_conversation", respond):
            # Exercise the turn-limit checkpoint without changing production's
            # configured limit by supplying ten already-recognized messages.
            messages = iter(["hello"] * 10)

            def next_message(*_args, **_kwargs):
                try:
                    return next(messages)
                except StopIteration:
                    return "stop now full stop"

            listen.side_effect = next_message
            conversation.start_voice_conversation()

        self.assertEqual(10, respond.call_count)
        speak.assert_any_call("Conversation mode ended. Standing by.")


class ConversationVoiceExperimentTests(unittest.TestCase):
    def test_missing_config_keeps_experiment_disabled(self):
        missing = Path("does-not-exist-conversation-voice.json")
        config = conversation_voice.load_conversation_voice_config(missing)

        self.assertFalse(config["enabled"])

    def test_sentence_chunking_preserves_remaining_text(self):
        chunks, remaining = conversation_voice._split_ready_chunks(
            "This is the first complete sentence. This part is unfinished",
            minimum_characters=20,
            maximum_characters=80,
        )

        self.assertEqual(["This is the first complete sentence."], chunks)
        self.assertEqual("This part is unfinished", remaining)

    @patch("conversation.chat_with_clap", return_value="Established response.")
    @patch("conversation.speak")
    @patch("conversation.load_conversation_voice_config")
    def test_disabled_experiment_uses_established_flow(
        self,
        load_config,
        speak,
        chat,
    ):
        load_config.return_value = {
            "enabled": False,
            "backend": "ollama_sentence_stream",
        }

        response = conversation.respond_in_conversation("hello")

        self.assertEqual("Established response.", response)
        chat.assert_called_once_with("hello")
        speak.assert_called_once_with("Established response.")

    @patch("conversation.chat_with_clap", return_value="Fallback response.")
    @patch("conversation.speak")
    @patch("conversation.stream_and_speak_conversation", return_value=None)
    @patch("conversation.load_conversation_voice_config")
    def test_stream_failure_uses_established_fallback(
        self,
        load_config,
        stream_response,
        speak,
        chat,
    ):
        load_config.return_value = {
            "enabled": True,
            "backend": "ollama_sentence_stream",
            "minimum_chunk_characters": 48,
            "maximum_chunk_characters": 180,
        }

        response = conversation.respond_in_conversation("hello")

        self.assertEqual("Fallback response.", response)
        stream_response.assert_called_once()
        chat.assert_called_once_with("hello")
        speak.assert_called_once_with("Fallback response.")


class PromptPrecedenceTests(unittest.TestCase):
    def test_direct_questions_take_precedence_over_profile_goals(self):
        self.assertIn(
            "Answer a direct question directly before offering anything else.",
            conversation.SYSTEM_PROMPT,
        )
        self.assertIn(
            "Do not redirect a direct question into coaching",
            conversation.SYSTEM_PROMPT,
        )

    def test_profile_cannot_trigger_a_mode_without_explicit_request(self):
        self.assertIn(
            "These facts are background context only.",
            conversation.private_context,
        )
        self.assertIn(
            "unless the user explicitly asks for it",
            conversation.private_context,
        )


if __name__ == "__main__":
    unittest.main()
