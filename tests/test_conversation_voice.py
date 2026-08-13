import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import conversation_voice


class FakeStreamingResponse:
    def __init__(self, events):
        self.events = events

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        return False

    def raise_for_status(self):
        return None

    def iter_lines(self):
        return [json.dumps(event).encode("utf-8") for event in self.events]


class OllamaSentenceStreamingTests(unittest.TestCase):
    @patch("conversation_voice.requests.post")
    def test_json_lines_are_emitted_as_voice_chunks(self, post):
        post.return_value = FakeStreamingResponse(
            [
                {"message": {"content": "This is the first sentence. "}},
                {"message": {"content": "This is the second sentence."}},
            ]
        )

        chunks = list(
            conversation_voice.stream_ollama_sentences(
                url="http://localhost:11434/api/chat",
                model="test-model",
                messages=[{"role": "user", "content": "hello"}],
                options={},
                minimum_characters=10,
                maximum_characters=80,
            )
        )

        self.assertEqual(
            ["This is the first sentence.", "This is the second sentence."],
            chunks,
        )
        self.assertTrue(post.call_args.kwargs["stream"])
        self.assertFalse(post.call_args.kwargs["json"]["think"])

    @patch("conversation_voice.stream_ollama_sentences")
    def test_streamed_chunks_are_spoken_and_saved_to_history(self, stream):
        stream.return_value = iter(("First response.", "Second response."))
        history = [{"role": "system", "content": "system"}]
        spoken = []

        response = conversation_voice.stream_and_speak_conversation(
            user_message="hello",
            conversation_history=history,
            url="http://localhost:11434/api/chat",
            model="test-model",
            options={},
            speak=lambda chunk: spoken.append(chunk) or True,
            direct_address=lambda chunk: chunk,
            config={
                "minimum_chunk_characters": 10,
                "maximum_chunk_characters": 80,
            },
        )

        self.assertEqual("First response. Second response.", response)
        self.assertEqual(["First response.", "Second response."], spoken)
        self.assertEqual("user", history[-2]["role"])
        self.assertEqual("assistant", history[-1]["role"])


if __name__ == "__main__":
    unittest.main()
