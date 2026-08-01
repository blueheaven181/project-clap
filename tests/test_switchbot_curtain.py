import asyncio
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import command_router
import switchbot_curtain
from switchbot_curtain import (
    GET_STATUS_PAYLOAD,
    STOP_PAYLOAD,
    SwitchBotCurtain,
    build_position_payload,
    load_local_config,
    parse_curtain_intent,
    parse_status_response,
    validate_position,
)
from switchbot_curtain_discovery import is_curtain_3_advertisement


class FakeDevice:
    def __init__(self, name=None):
        self.name = name


class FakeAdvertisement:
    def __init__(self, local_name=None, service_data=None):
        self.local_name = local_name
        self.service_data = service_data or {}


class FakeBleakClient:
    response = bytes((1, 80, 42, 1, 0, 4, 50, 0))
    last_payload = None

    def __init__(self, address, timeout):
        self.address = address
        self.timeout = timeout
        self.callback = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def start_notify(self, _characteristic, callback):
        self.callback = callback

    async def write_gatt_char(self, _characteristic, payload, response):
        self.__class__.last_payload = payload
        self.callback(None, self.__class__.response)


class SilentBleakClient(FakeBleakClient):
    async def write_gatt_char(self, _characteristic, payload, response):
        self.__class__.last_payload = payload


class CurtainIntentTests(unittest.TestCase):
    def test_supported_natural_intents(self):
        expected = {
            "Open the curtain.": "open",
            "Please close my curtains": "close",
            "What position is the curtain?": "status",
            "How open are my curtains?": "status",
            "Set the curtain to 50 percent.": "set_position",
            "Move my curtains at 25 percentage": "set_position",
            "Stop the curtain.": "stop",
        }
        for phrase, action in expected.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(parse_curtain_intent(phrase)["action"], action)

    def test_untrusted_or_ai_style_commands_are_rejected(self):
        for phrase in (
            "Open the window",
            "Do something with the curtain",
            "Run raw curtain payload 570f450105ff00",
            "Could you maybe open the curtain later",
        ):
            self.assertIsNone(parse_curtain_intent(phrase))
            self.assertFalse(command_router.is_switchbot_curtain_request(phrase))

    def test_position_validation(self):
        self.assertEqual(validate_position(0), 0)
        self.assertEqual(validate_position(100), 100)
        for value in (-1, 101, 50.5, "50", True):
            with self.assertRaises(ValueError):
                validate_position(value)

    def test_out_of_range_transcript_stays_trusted_for_safe_rejection(self):
        request = parse_curtain_intent("Set the curtain to 101 percent")
        self.assertEqual(request, {"action": "set_position", "position": 101})
        self.assertTrue(command_router.is_switchbot_curtain_request("Set the curtain to -1 percent"))


class CurtainDiscoveryTests(unittest.TestCase):
    def test_named_curtain_is_recognized(self):
        self.assertTrue(
            is_curtain_3_advertisement(
                FakeDevice("WoCurtain3"), FakeAdvertisement()
            )
        )

    def test_unnamed_curtain_3_service_data_is_recognized(self):
        self.assertTrue(
            is_curtain_3_advertisement(
                FakeDevice(),
                FakeAdvertisement(
                    service_data={
                        "0000fd3d-0000-1000-8000-00805f9b34fb": b"\x7b\x40"
                    }
                ),
            )
        )

    def test_other_switchbot_device_is_rejected(self):
        self.assertFalse(
            is_curtain_3_advertisement(
                FakeDevice(),
                FakeAdvertisement(service_data={"fd3d": b"\x48\x40"}),
            )
        )


class CurtainProtocolTests(unittest.TestCase):
    def test_official_ble_payloads(self):
        self.assertEqual(GET_STATUS_PAYLOAD, bytes.fromhex("5702"))
        self.assertEqual(build_position_payload(0), bytes.fromhex("570f450105ff00"))
        self.assertEqual(build_position_payload(50), bytes.fromhex("570f450105ff32"))
        self.assertEqual(build_position_payload(100), bytes.fromhex("570f450105ff64"))
        self.assertEqual(STOP_PAYLOAD, bytes.fromhex("570f4500ff"))

    def test_status_response(self):
        status = parse_status_response(bytes((1, 80, 42, 1, 0, 5, 50, 0)))
        self.assertEqual(status["position"], 50)
        self.assertTrue(status["calibrated"])
        self.assertTrue(status["moving"])

    def test_malformed_and_offline_responses_fail_safely(self):
        with self.assertRaises(ValueError):
            parse_status_response(b"\x01")
        with self.assertRaises(RuntimeError):
            parse_status_response(bytes((3, 0, 0, 0, 0, 0, 0, 0)))

    def test_ble_client_sends_only_prebuilt_payload(self):
        curtain = SwitchBotCurtain("private-address", client_factory=FakeBleakClient)
        asyncio.run(curtain.set_position(50))
        self.assertEqual(FakeBleakClient.last_payload, build_position_payload(50))

    @patch("switchbot_curtain.RESPONSE_TIMEOUT_SECONDS", 0.001)
    def test_ble_timeout(self):
        curtain = SwitchBotCurtain("private-address", client_factory=SilentBleakClient)
        with self.assertRaises(TimeoutError):
            asyncio.run(curtain.stop())

    def test_missing_and_malformed_local_configuration(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "switchbot.local.json"
            with self.assertRaises(FileNotFoundError):
                load_local_config(path)
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_local_config(path)


class CurtainRoutingTests(unittest.TestCase):
    @patch("command_router.speak")
    @patch("command_router.set_curtain_position")
    @patch("command_router.listen_until_response", return_value="yes yes yes")
    def test_repeated_yes_moves_curtain(self, _listen, move, _speak):
        self.assertTrue(command_router.route_command("Open the curtain"))
        move.assert_called_once_with(0)

    @patch("command_router.speak")
    @patch("command_router.set_curtain_position")
    @patch("command_router.listen_until_response", return_value="yes yes no")
    def test_mixed_confirmation_cancels(self, _listen, move, _speak):
        self.assertTrue(command_router.route_command("Close the curtain"))
        move.assert_not_called()

    @patch("command_router.speak")
    @patch("command_router.stop_curtain")
    @patch("command_router.listen_until_response", return_value="")
    def test_failed_speech_never_sends_stop(self, _listen, stop, _speak):
        self.assertTrue(command_router.route_command("Stop my curtain"))
        stop.assert_not_called()

    @patch("command_router.speak")
    @patch("command_router.set_curtain_position")
    def test_invalid_position_does_not_request_confirmation_or_move(self, move, _speak):
        self.assertTrue(command_router.route_command("Set curtain to 150 percent"))
        move.assert_not_called()

    @patch("command_router.speak")
    @patch("command_router.get_curtain_status", return_value="The curtain is at 50 percent closed.")
    def test_status_read_does_not_require_confirmation(self, status, _speak):
        self.assertTrue(command_router.route_command("What is the curtain position?"))
        status.assert_called_once_with()

    @patch("command_router.speak")
    @patch("command_router.get_weather", return_value="Weather still works.")
    def test_existing_command_regression(self, weather, _speak):
        self.assertTrue(command_router.route_command("weather"))
        weather.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
