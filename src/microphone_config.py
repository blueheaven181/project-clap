"""Select CLAP's microphone by stable name instead of volatile device index."""


PREFERRED_MICROPHONE_NAME = "fifine microphone"


def select_sounddevice_input(devices, preferred=PREFERRED_MICROPHONE_NAME):
    """Return the preferred input index, or the first usable input device."""

    preferred = preferred.casefold()
    fallback = None
    for index, device in enumerate(devices):
        if int(device.get("max_input_channels", 0)) < 1:
            continue
        if fallback is None:
            fallback = index
        if preferred in str(device.get("name", "")).casefold():
            return index
    if fallback is None:
        raise RuntimeError("No usable microphone input was found.")
    return fallback


def select_named_microphone(names, preferred=PREFERRED_MICROPHONE_NAME):
    """Return a speech-recognition device index using the preferred name."""

    preferred = preferred.casefold()
    for index, name in enumerate(names):
        if preferred in str(name).casefold():
            return index
    return None
