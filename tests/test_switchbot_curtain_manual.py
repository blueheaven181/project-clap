import sys
import unittest
from pathlib import Path
from unittest.mock import Mock


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from switchbot_curtain_manual_test import run_position_test


class CurtainManualHardwareUtilityTests(unittest.TestCase):
    def test_exact_target_confirmation_sends_one_command(self):
        move = Mock(return_value="accepted")

        result = run_position_test(
            100,
            input_func=lambda _prompt: "MOVE CURTAIN TO 100",
            move_func=move,
        )

        self.assertEqual(result, "accepted")
        move.assert_called_once_with(100)

    def test_mismatched_confirmation_sends_nothing(self):
        move = Mock()

        result = run_position_test(
            100,
            input_func=lambda _prompt: "yes",
            move_func=move,
        )

        self.assertEqual(result, "Cancelled. No Curtain command was sent.")
        move.assert_not_called()

    def test_invalid_position_is_rejected_before_confirmation(self):
        move = Mock()
        prompted = Mock(return_value="MOVE CURTAIN TO 101")

        with self.assertRaises(ValueError):
            run_position_test(101, input_func=prompted, move_func=move)

        prompted.assert_not_called()
        move.assert_not_called()


if __name__ == "__main__":
    unittest.main()
