"""Read-only local discovery helper for SwitchBot Curtain setup."""

import asyncio

from bleak import BleakScanner


SWITCHBOT_SERVICE_UUIDS = {
    "0000fd3d-0000-1000-8000-00805f9b34fb",
    "fd3d",
}
CURTAIN_3_DEVICE_TYPE = 0x7B


def is_curtain_3_advertisement(device, advertisement):
    """Recognize Curtain 3 by name or official SwitchBot service data."""

    names = (device.name, advertisement.local_name)
    if any("curtain" in (name or "").lower() for name in names):
        return True

    for service_uuid, service_data in advertisement.service_data.items():
        if service_uuid.lower() not in SWITCHBOT_SERVICE_UUIDS or not service_data:
            continue
        if service_data[0] & 0x7F == CURTAIN_3_DEVICE_TYPE:
            return True
    return False


async def discover_curtain_candidates(timeout=8):
    """Return Curtain 3 candidates from names or official service data."""

    discovered = await BleakScanner.discover(timeout=timeout, return_adv=True)
    return [
        (device, advertisement)
        for device, advertisement in discovered.values()
        if is_curtain_3_advertisement(device, advertisement)
    ]


def main():
    print("Scanning locally for nearby Curtain devices...")
    try:
        devices = asyncio.run(discover_curtain_candidates())
    except Exception as error:
        print(f"Bluetooth discovery failed: {type(error).__name__}")
        return

    if not devices:
        print(
            "No Curtain 3 advertisements were found. Close the SwitchBot app's "
            "Curtain screen, move closer, and retry."
        )
        return

    print("Nearby Curtain candidates (keep these addresses private):")
    for device, advertisement in devices:
        name = device.name or advertisement.local_name or "Unnamed Curtain 3"
        print(f"- {name}: {device.address}")


if __name__ == "__main__":
    main()
