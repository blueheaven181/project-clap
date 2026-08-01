import sys
import unittest
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

from conversation import use_direct_personal_address


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


if __name__ == "__main__":
    unittest.main()
