"""Read-only local discovery helper for SwitchBot Curtain setup."""

import asyncio

from bleak import BleakScanner


async def discover_curtain_candidates(timeout=8):
    """Return nearby devices whose advertised name looks like a curtain."""

    devices = await BleakScanner.discover(timeout=timeout)
    return [
        device
        for device in devices
        if "curtain" in (device.name or "").lower()
        or "wocurtain" in (device.name or "").lower()
    ]


def main():
    print("Scanning locally for nearby Curtain devices...")
    try:
        devices = asyncio.run(discover_curtain_candidates())
    except Exception as error:
        print(f"Bluetooth discovery failed: {type(error).__name__}")
        return

    if not devices:
        print("No named Curtain candidates were found. Move closer and retry.")
        return

    print("Nearby Curtain candidates (keep these addresses private):")
    for device in devices:
        print(f"- {device.name or 'Unnamed Curtain'}: {device.address}")


if __name__ == "__main__":
    main()
