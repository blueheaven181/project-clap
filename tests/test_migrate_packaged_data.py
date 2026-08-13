import tempfile
import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from migrate_packaged_data import migrate_private_data


class PrivateDataMigrationTests(unittest.TestCase):
    def test_copies_only_allowlisted_files_without_overwriting(self):
        with tempfile.TemporaryDirectory() as source_temp, tempfile.TemporaryDirectory() as dest_temp:
            source = Path(source_temp)
            destination = Path(dest_temp)
            (source / "config").mkdir()
            (source / "assets").mkdir()
            (source / "config" / "credentials.json").write_text("source")
            (source / "config" / "token.revoked.json").write_text("do not copy")
            (source / "assets" / "briefing_music.mp3").write_bytes(b"music")
            (destination / "config").mkdir()
            existing = destination / "config" / "credentials.json"
            existing.write_text("destination")

            result = migrate_private_data(source, destination)

            self.assertEqual(existing.read_text(), "destination")
            self.assertFalse((destination / "config" / "token.revoked.json").exists())
            self.assertEqual(
                (destination / "assets" / "briefing_music.mp3").read_bytes(),
                b"music",
            )
            self.assertIn("config\\credentials.json", result["skipped_existing"])


if __name__ == "__main__":
    unittest.main()
