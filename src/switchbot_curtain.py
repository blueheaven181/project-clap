"""Trusted local-Bluetooth control for a SwitchBot Curtain 3."""

import asyncio
import json
import re
import threading
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "switchbot.local.json"
WRITE_CHARACTERISTIC = "cba20002-224d-11e6-9fb8-0002a5d5c51b"
NOTIFY_CHARACTERISTIC = "cba20003-224d-11e6-9fb8-0002a5d5c51b"
CONNECT_TIMEOUT_SECONDS = 8
RESPONSE_TIMEOUT_SECONDS = 5
DISCONNECT_TIMEOUT_SECONDS = 3
SWITCHBOT_SERVICE_UUIDS = {
    "0000fd3d-0000-1000-8000-00805f9b34fb",
    "fd3d",
}
CURTAIN_3_DEVICE_TYPE = 0x7B

GET_STATUS_PAYLOAD = bytes.fromhex("5702")
STOP_PAYLOAD = bytes.fromhex("570f45010001")

RESPONSE_ERRORS = {
    0x02: "The curtain rejected the command.",
    0x03: "The curtain is busy. Please try again shortly.",
    0x04: "The curtain firmware uses an incompatible Bluetooth protocol.",
    0x05: "The curtain does not support that command.",
    0x06: "The curtain battery is too low to perform that command.",
    0x0D: "The curtain cannot perform that command in its current mode.",
    0x0E: "The curtain Bluetooth connection was interrupted.",
}


class CurtainBluetoothError(RuntimeError):
    """A redacted BLE failure annotated with its pre/post-command phase."""


class CurtainResponseError(RuntimeError):
    """A safe Curtain protocol rejection that may be shown to the user."""


def _response_error(code):
    message = RESPONSE_ERRORS.get(code, "The curtain returned an unknown error.")
    return CurtainResponseError(f"{message} (response code 0x{code:02X})")


def _redact_private_value(message, private_value):
    return str(message).replace(private_value, "[private device]")


def parse_curtain_intent(command):
    """Return an explicitly supported Curtain command or None."""

    normalized = re.sub(r"\s+", " ", command.strip().lower())
    if not re.search(r"\bcurtains?\b", normalized):
        return None

    position_match = re.fullmatch(
        r"(?:please )?(?:set|move|open|close) (?:the |my )?curtains?"
        r"(?: (?:to|at))? (-?\d+(?:\.\d+)?) ?(?:percent|percentage|%)?[.!?]?",
        normalized,
    )
    if position_match:
        value = float(position_match.group(1))
        if not value.is_integer():
            return {"action": "invalid_position", "position": value}
        return {"action": "set_position", "position": int(value)}

    patterns = {
        "status": (
            r"(?:what|which) (?:is )?(?:the |my )?curtains? (?:position|status)",
            r"(?:what|which) position (?:is|are) (?:the |my )?curtains?",
            r"how (?:open|closed) (?:is|are) (?:the |my )?curtains?",
            r"check (?:the |my )?curtains? (?:position|status)",
        ),
        "open": (r"open (?:the |my )?curtains?",),
        "close": (r"close (?:the |my )?curtains?",),
        "stop": (
            r"stop (?:the |my )?curtains?",
            r"stop (?:the |my )?curtains? movement",
        ),
    }
    stripped = normalized.rstrip(".!?")
    for action, action_patterns in patterns.items():
        if any(re.fullmatch(rf"(?:please )?{pattern}", stripped) for pattern in action_patterns):
            return {"action": action}
    return None


def validate_position(position):
    """Validate a Curtain 3 position, where 0 is open and 100 is closed."""

    if isinstance(position, bool) or not isinstance(position, (int, float)):
        raise ValueError("Curtain position must be a whole number from 0 to 100.")
    if not float(position).is_integer() or position < 0 or position > 100:
        raise ValueError("Curtain position must be a whole number from 0 to 100.")
    return int(position)


def build_position_payload(position, speed=0xFF):
    """Build the official Curtain 3 BLE set-position packet."""

    position = validate_position(position)
    if speed not in (0x00, 0x01, 0xFF):
        raise ValueError("Unsupported Curtain 3 movement speed.")
    return bytes((0x57, 0x0F, 0x45, 0x01, 0x05, speed, position))


def parse_status_response(response):
    """Parse an official Curtain 3 basic-information response."""

    if not isinstance(response, (bytes, bytearray)) or len(response) < 8:
        raise ValueError("The curtain returned a malformed status response.")
    if response[0] != 0x01:
        raise _response_error(response[0])
    position = response[6]
    if position > 100:
        raise ValueError("The curtain returned an invalid position.")
    state = response[5]
    return {
        "battery": response[1],
        "calibrated": bool(state & 0b00000100),
        "moving": bool(state & 0b00000011),
        "position": position,
    }


def parse_advertisement_status(service_data):
    """Parse Curtain 3 status from its official connection-free broadcast."""

    if not isinstance(service_data, (bytes, bytearray)) or len(service_data) < 4:
        raise ValueError("The curtain returned malformed Bluetooth status data.")
    if service_data[0] & 0x7F != CURTAIN_3_DEVICE_TYPE:
        raise ValueError("The Bluetooth status data is not from a Curtain 3.")
    position_byte = service_data[3]
    position = position_byte & 0x7F
    if position > 100:
        raise ValueError("The curtain returned an invalid position.")
    return {
        "battery": service_data[2] & 0x7F,
        "calibrated": bool(service_data[1] & 0x40),
        "moving": bool(position_byte & 0x80),
        "position": position,
    }


async def read_advertised_status(address, discover=None):
    """Read status from the configured Curtain's BLE advertisement."""

    if discover is None:
        try:
            from bleak import BleakScanner
        except ImportError as error:
            raise RuntimeError("Bluetooth support is not installed.") from error
        discover = BleakScanner.discover

    discovered = await discover(timeout=CONNECT_TIMEOUT_SECONDS, return_adv=True)
    for device, advertisement in discovered.values():
        if device.address.casefold() != address.casefold():
            continue
        for service_uuid, service_data in advertisement.service_data.items():
            if service_uuid.lower() in SWITCHBOT_SERVICE_UUIDS:
                return parse_advertisement_status(service_data)
        raise ValueError("The curtain advertisement did not contain status data.")
    raise TimeoutError("The configured curtain was not found during Bluetooth discovery.")


def load_local_config(path=CONFIG_PATH):
    """Load the ignored local Bluetooth address without logging it."""

    if not path.exists():
        raise FileNotFoundError("SwitchBot local configuration was not found.")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("SwitchBot local configuration is invalid.") from error
    address = config.get("bluetooth_address")
    if not isinstance(address, str) or not address.strip():
        raise ValueError("SwitchBot Bluetooth address is missing from local configuration.")
    return {"bluetooth_address": address.strip()}


class SwitchBotCurtain:
    """Small BLE client restricted to official Curtain 3 packets."""

    def __init__(self, address, client_factory=None, device_resolver=None):
        self.address = address
        self.client_factory = client_factory
        self.device_resolver = device_resolver

    async def _send(self, payload):
        phase = "loading Bluetooth support"
        if self.client_factory is None:
            try:
                from bleak import BleakClient, BleakScanner
            except ImportError as error:
                raise RuntimeError("Bluetooth support is not installed.") from error
            client_factory = BleakClient
            device_resolver = BleakScanner.find_device_by_address
        else:
            client_factory = self.client_factory
            device_resolver = self.device_resolver

        try:
            phase = "resolving the configured device"
            device = self.address
            if device_resolver is not None:
                device = await device_resolver(
                    self.address,
                    timeout=CONNECT_TIMEOUT_SECONDS,
                )
                if device is None:
                    raise TimeoutError(
                        "The configured curtain was not found during Bluetooth discovery."
                    )

            response_future = asyncio.get_running_loop().create_future()
        except TimeoutError:
            raise
        except Exception as error:
            detail = _redact_private_value(error, self.address)
            raise CurtainBluetoothError(
                f"Bluetooth failed while {phase}: {type(error).__name__}: {detail}"
            ) from error

        def receive_response(_sender, data):
            if not response_future.done():
                response_future.set_result(bytes(data))

        client = client_factory(device, timeout=CONNECT_TIMEOUT_SECONDS)
        try:
            phase = "connecting"
            await client.connect()
            phase = "resolving required GATT characteristics"
            write_characteristic = client.services.get_characteristic(
                WRITE_CHARACTERISTIC
            )
            notify_characteristic = client.services.get_characteristic(
                NOTIFY_CHARACTERISTIC
            )
            if write_characteristic is None or notify_characteristic is None:
                raise CurtainBluetoothError(
                    "The connected curtain did not expose the required GATT characteristics."
                )
            phase = "subscribing for the device response"
            await client.start_notify(notify_characteristic, receive_response)
            phase = "writing the trusted command"
            await client.write_gatt_char(write_characteristic, payload, response=False)
            phase = "waiting for the device response"
            return await asyncio.wait_for(response_future, RESPONSE_TIMEOUT_SECONDS)
        except asyncio.TimeoutError as error:
            raise TimeoutError("The curtain did not respond before the Bluetooth timeout.") from error
        except Exception as error:
            detail = _redact_private_value(error, self.address)
            raise CurtainBluetoothError(
                f"Bluetooth failed while {phase}: {type(error).__name__}: {detail}"
            ) from error
        finally:
            if client.is_connected:
                try:
                    await asyncio.wait_for(
                        client.disconnect(),
                        DISCONNECT_TIMEOUT_SECONDS,
                    )
                except Exception as error:
                    print("SwitchBot Curtain cleanup:", type(error).__name__)

    async def get_status(self):
        return parse_status_response(await self._send(GET_STATUS_PAYLOAD))

    async def set_position(self, position):
        response = await self._send(build_position_payload(position))
        self._validate_action_response(response)

    async def stop(self):
        response = await self._send(STOP_PAYLOAD)
        self._validate_action_response(response)

    @staticmethod
    def _validate_action_response(response):
        if not response:
            raise ValueError("The curtain returned a malformed response.")
        if response[0] != 0x01:
            raise _response_error(response[0])


def _run(operation):
    outcome = {}

    def run_bluetooth_operation():
        try:
            outcome["result"] = asyncio.run(operation)
        except BaseException as error:
            outcome["error"] = error

    try:
        config = load_local_config()
        curtain = SwitchBotCurtain(config["bluetooth_address"])
        operation = operation(curtain)
        worker = threading.Thread(
            target=run_bluetooth_operation,
            name="switchbot-curtain-bluetooth",
        )
        worker.start()
        worker.join()
        if "error" in outcome:
            raise outcome["error"]
        return outcome["result"]
    except FileNotFoundError:
        return "SwitchBot is not configured. Please complete the local Bluetooth setup."
    except ValueError as error:
        return str(error)
    except TimeoutError:
        return "The curtain did not respond. Check Bluetooth, range, and whether the device is offline."
    except CurtainBluetoothError as error:
        print("SwitchBot Curtain diagnostic:", error)
        return "I could not connect to the curtain over Bluetooth."
    except CurtainResponseError as error:
        print("SwitchBot Curtain diagnostic:", error)
        return str(error)
    except Exception as error:
        print("SwitchBot Curtain error:", type(error).__name__)
        return "I could not connect to the curtain over Bluetooth."


def get_curtain_status():
    async def operation(curtain):
        status = await read_advertised_status(curtain.address)
        if not status["calibrated"]:
            return "The curtain is connected but is not calibrated."
        movement = " and is moving" if status["moving"] else ""
        return f"The curtain is at {status['position']} percent closed{movement}."
    return _run(operation)


def set_curtain_position(position):
    try:
        position = validate_position(position)
    except ValueError as error:
        return str(error)

    async def operation(curtain):
        await curtain.set_position(position)
        if position == 0:
            return "The curtain is opening."
        if position == 100:
            return "The curtain is closing."
        return f"The curtain is moving to {position} percent closed."
    return _run(operation)


def stop_curtain():
    async def operation(curtain):
        await curtain.stop()
        return "Curtain movement stopped."
    return _run(operation)
