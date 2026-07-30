from pycaw.pycaw import AudioUtilities


def get_volume_interface():
    """
    Return the Windows master-volume interface.
    """

    speakers = AudioUtilities.GetSpeakers()
    return speakers.EndpointVolume


def get_system_volume():
    """
    Return the current Windows volume as a whole percentage.
    """

    volume = get_volume_interface()
    current_level = volume.GetMasterVolumeLevelScalar()

    return round(current_level * 100)


def set_system_volume(percentage):
    """
    Set Windows volume to an exact percentage from 0 to 100.
    """

    safe_percentage = max(0, min(100, float(percentage)))

    volume = get_volume_interface()
    volume.SetMasterVolumeLevelScalar(
        safe_percentage / 100,
        None,
    )

    final_percentage = round(safe_percentage)

    print(f"System volume set to {final_percentage} percent.")
    return final_percentage


def change_system_volume(change):
    """
    Increase or decrease Windows volume by percentage points.
    """

    current_percentage = get_system_volume()
    target_percentage = current_percentage + float(change)

    return set_system_volume(target_percentage)


def mute_system_volume():
    """
    Mute Windows system audio.
    """

    volume = get_volume_interface()
    volume.SetMute(1, None)

    print("System audio muted.")


def unmute_system_volume():
    """
    Unmute Windows system audio.
    """

    volume = get_volume_interface()
    volume.SetMute(0, None)

    print("System audio unmuted.")


if __name__ == "__main__":
    print(f"Current system volume: {get_system_volume()} percent.")