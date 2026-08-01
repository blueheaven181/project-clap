"""Read-only Windows BLE diagnostic for the configured Curtain 3."""

import asyncio

from bleak import BleakClient, BleakScanner

from switchbot_curtain import (
    CONNECT_TIMEOUT_SECONDS,
    GET_STATUS_PAYLOAD,
    NOTIFY_CHARACTERISTIC,
    RESPONSE_TIMEOUT_SECONDS,
    WRITE_CHARACTERISTIC,
    load_local_config,
)


def _safe_message(error, private_address):
    message = str(error).replace(private_address, "[private device]")
    return message or "No additional details were provided."


async def diagnose(address):
    print("1. Scanning for the configured Curtain...")
    device = await BleakScanner.find_device_by_address(
        address,
        timeout=CONNECT_TIMEOUT_SECONDS,
    )
    if device is None:
        print("Result: configured Curtain was not visible during this scan.")
        return

    print("2. Configured Curtain found. Connecting without sending commands...")
    client = BleakClient(device, timeout=CONNECT_TIMEOUT_SECONDS)
    await client.connect()
    try:
        print("3. Connected. Inspecting required GATT characteristics...")
        write_characteristic = client.services.get_characteristic(
            WRITE_CHARACTERISTIC
        )
        notify_characteristic = client.services.get_characteristic(
            NOTIFY_CHARACTERISTIC
        )
        print("write_characteristic_present=", bool(write_characteristic))
        print("notify_characteristic_present=", bool(notify_characteristic))
        if write_characteristic:
            print("write_properties=", sorted(write_characteristic.properties))
        if notify_characteristic:
            print("notify_properties=", sorted(notify_characteristic.properties))
            print("4. Testing notification subscription without sending data...")
            response = asyncio.get_running_loop().create_future()

            def receive_response(_sender, data):
                if not response.done():
                    response.set_result(bytes(data))

            await client.start_notify(notify_characteristic, receive_response)
            print("notification_subscription= successful")
            if write_characteristic:
                print("5. Sending read-only status request...")
                await client.write_gatt_char(
                    write_characteristic,
                    GET_STATUS_PAYLOAD,
                    response=False,
                )
                status_response = await asyncio.wait_for(
                    response,
                    RESPONSE_TIMEOUT_SECONDS,
                )
                print("status_notification_received=", bool(status_response))
            await client.stop_notify(notify_characteristic)
    finally:
        if client.is_connected:
            try:
                await asyncio.wait_for(client.disconnect(), 3)
                print("6. Disconnect completed.")
            except Exception as error:
                print("6. Disconnect cleanup:", type(error).__name__)


def main():
    try:
        address = load_local_config()["bluetooth_address"]
    except Exception as error:
        print(f"Configuration error: {type(error).__name__}")
        return

    try:
        asyncio.run(diagnose(address))
    except Exception as error:
        print(f"Diagnostic error type: {type(error).__name__}")
        print("Diagnostic detail:", _safe_message(error, address))


if __name__ == "__main__":
    main()
