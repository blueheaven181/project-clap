import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import command_router
import forex


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"rates": {"AED": 4.0, "PHP": 64.0}}


class ForexConversionTests(unittest.TestCase):
    @patch("forex.requests.get", return_value=FakeResponse())
    def test_php_to_aed_calculation(self, _get):
        self.assertEqual(
            "15000 Philippine pesos is approximately 937.50 UAE dirhams.",
            forex.convert_php_to_aed(15000),
        )

    @patch("command_router.speak")
    @patch("command_router.convert_php_to_aed", return_value="PHP to AED")
    @patch("command_router.convert_aed_to_php", return_value="AED to PHP")
    def test_pesos_before_dirhams_selects_php_to_aed(
        self, aed_to_php, php_to_aed, _speak
    ):
        self.assertTrue(
            command_router.route_command(
                "how much 15000 Philippine peso in dirhams"
            )
        )
        php_to_aed.assert_called_once_with(15000.0)
        aed_to_php.assert_not_called()

    @patch("command_router.speak")
    @patch("command_router.convert_php_to_aed", return_value="PHP to AED")
    @patch("command_router.convert_aed_to_php", return_value="AED to PHP")
    def test_dirhams_before_pesos_preserves_aed_to_php(
        self, aed_to_php, php_to_aed, _speak
    ):
        self.assertTrue(
            command_router.route_command("how much is 100 dirhams in pesos")
        )
        aed_to_php.assert_called_once_with(100.0)
        php_to_aed.assert_not_called()


if __name__ == "__main__":
    unittest.main()
