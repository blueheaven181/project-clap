"""Copy approved private CLAP data into the packaged app data folder."""

import shutil
from pathlib import Path

from runtime_paths import PACKAGED_DATA_ROOT, SOURCE_ROOT


PRIVATE_CONFIG_FILES = (
    "conversation_voice.local.json",
    "credentials.json",
    "marc_profile.local.json",
    "presence.local.json",
    "speech_voice.local.json",
    "spotify_api.local.json",
    "spotify_playlists.local.json",
    "spotify_token.local.json",
    "switchbot.local.json",
    "token.json",
    "wake_word.local.json",
)


def migrate_private_data(source_root=SOURCE_ROOT, destination_root=PACKAGED_DATA_ROOT):
    """Copy approved files without reading contents or overwriting a destination."""

    source_root = Path(source_root).resolve()
    destination_root = Path(destination_root).resolve()
    copied = []
    skipped_existing = []
    absent = []

    pairs = [
        (source_root / "config" / name, destination_root / "config" / name)
        for name in PRIVATE_CONFIG_FILES
    ]
    pairs.append(
        (
            source_root / "assets" / "briefing_music.mp3",
            destination_root / "assets" / "briefing_music.mp3",
        )
    )

    for source, destination in pairs:
        label = str(destination.relative_to(destination_root))
        if not source.is_file():
            absent.append(label)
            continue
        if destination.exists():
            skipped_existing.append(label)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(label)

    return {
        "destination": destination_root,
        "copied": copied,
        "skipped_existing": skipped_existing,
        "absent": absent,
    }


def main():
    result = migrate_private_data()
    print("Project CLAP private-data migration")
    print("Destination:", result["destination"])
    print("Copied:", len(result["copied"]))
    print("Already present (not overwritten):", len(result["skipped_existing"]))
    print("Optional files absent:", len(result["absent"]))


if __name__ == "__main__":
    main()
