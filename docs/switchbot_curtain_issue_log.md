# SwitchBot Curtain 3 Issue and Resolution Log

This sanitized record preserves the initial local-Bluetooth integration history
without including the private Bluetooth address, account data, or local
configuration values. The repository remains the source of truth for the final
implementation.

## Discovery Found No Named Curtain

- **Symptom:** The first local scan reported no named Curtain candidates.
- **Cause:** Curtain 3 advertised without a human-readable device name.
- **Resolution:** Discovery now recognizes the official SwitchBot service-data
  device type as well as named advertisements.
- **Verification:** The installed unnamed Curtain 3 was discovered locally.

## Missing or Placeholder Local Address

- **Symptom:** Status could not locate the configured device until the discovered
  Windows BLE address replaced the example placeholder.
- **Resolution:** The real address is stored only in
  `config/switchbot.local.json`; the example remains sanitized.
- **Verification:** Git confirmed the local file is ignored, and tracked-file
  scans found no private address.

## Device Not Found or Status Timeout

- **Symptoms:** `BleakDeviceNotFoundError` and status timeouts occurred despite
  the Curtain being nearby.
- **Causes:** Windows BLE cache state, connection contention, and using a GATT
  connection for information already present in advertisements.
- **Resolution:** Connections resolve a fresh scanned device object. Routine
  status reads use the configured Curtain's official advertisement instead of
  opening GATT.
- **Verification:** Status repeatedly reported exact installed positions without
  movement.

## Intermittent GATT Unreachable

- **Symptom:** Windows found the Curtain but sometimes returned `Unreachable`
  while loading GATT services.
- **Cause:** The iPhone app could hold the active device connection, or Windows
  Bluetooth could retain a transient service state.
- **Resolution:** Close the iPhone's active Curtain screen, allow Windows and the
  phone to take turns, and use the read-only diagnostic before a new command.
  Toggling Windows Bluetooth is a recovery step, not an automatic command retry.
- **Verification:** The diagnostic connected, resolved both characteristics,
  subscribed, received status, and disconnected cleanly.

## Notification or Write Stalls

- **Symptom:** A connection could succeed without receiving the expected command
  result.
- **Cause:** The Curtain protocol writes without a GATT acknowledgement and then
  responds on its notification characteristic.
- **Resolution:** Subscribe first, write with response disabled, then wait up to
  five seconds for one notification.
- **Verification:** Read-only and movement responses were received on real
  hardware.

## Missing Notification Characteristic During Live Control

- **Symptom:** Live control raised `BleakCharacteristicNotFoundError` even though
  the diagnostic had previously found the characteristic.
- **Cause:** Passing UUID text made Bleak repeat the characteristic lookup against
  Windows' transient service view.
- **Resolution:** Live control resolves the characteristic objects from the
  connected service collection and passes those objects to notification and
  write operations. Missing characteristics fail before a movement write.
- **Verification:** Subsequent trusted movement commands connected and completed.

## Windows COM Threading Conflict

- **Symptoms:** Bleak first reported that GUI-thread callbacks were unavailable.
  A temporary main-thread MTA setting then caused Windows audio imports to fail
  with “Cannot change thread mode after it is set.”
- **Cause:** Bleak WinRT callbacks and the system-volume dependency required
  incompatible COM handling on the same main thread.
- **Final resolution:** The temporary global MTA setting was removed. Curtain BLE
  operations now run on a dedicated worker thread with a private asyncio loop,
  leaving CLAP's audio and desktop dependencies on the main thread.
- **Verification:** Windows audio imports, Curtain BLE, and the complete automated
  suite pass together.

## Movement Rejected as Unsupported

- **Symptom:** The real Curtain returned protocol response `0x05` for position
  movement.
- **Cause:** The packet was missing the required Curtain command-family byte.
- **Resolution:** Position packets now include the maintained command-family and
  Curtain 3 action fields.
- **Verification:** Exact 10%, full Close, and full Open succeeded and were
  confirmed by advertisement status.

## Stop Rejected as Unsupported

- **Symptom:** Position movement worked, but the first Stop variant returned
  `0x05`.
- **Cause:** This installed Curtain 3 requires the maintained `...0001` Stop
  variant rather than `...00FF`.
- **Resolution:** The trusted Stop constant uses the device-proven variant.
- **Verification:** A move toward 50% stopped at 32%, and trusted voice Stop was
  accepted.

## Cleanup Error Masked a Successful Response

- **Symptom:** Disconnect cleanup could replace a successful Curtain result with
  an error.
- **Resolution:** Disconnect is bounded to three seconds, and cleanup failures
  cannot override a received success response.
- **Verification:** Automated cleanup-error regression coverage passes.

## Generic RuntimeError Hid Device Rejections

- **Symptom:** A safe protocol rejection was reported only as a generic Bluetooth
  connection failure.
- **Resolution:** Protocol rejections use a dedicated safe exception and preserve
  the non-private response code; transport errors retain redacted phase details.
- **Verification:** The unsupported position and Stop variants were diagnosed
  without exposing device identity.

## Curtain Command Opened an Unwanted Follow-Up Conversation

- **Symptom:** After a Curtain result, CLAP asked whether another command was
  needed and continued listening without a new activation.
- **Resolution:** Every Curtain command now ends its interaction and returns
  directly to wake-word standby.
- **Verification:** Status, accepted movement, cancellation, and failure paths all
  returned to “Listening for double clap or Hey CLAP.”

## Doubled or “Crowd” Speech

- **Symptoms:** Several CLAP voices appeared to speak and listen together; a
  hidden listener continued after the visible terminal returned.
- **Causes:** A lingering CLAP process and Windows `Ctrl+Z` not terminating the
  listener. Separately generated greeting clips also made playback less cohesive.
- **Resolution:** Use `Ctrl+C` to stop the listener. A Windows named mutex rejects
  a second CLAP listener, speech playback is serialized, and activation speech is
  generated as one clip.
- **Verification:** The lingering processes were removed, the one-shot speech
  test exited cleanly, and single-instance tests pass.

## Hardware Debugging Was Too Coupled to Full CLAP

- **Symptom:** Testing through wake word, speech, routing, COM, and BLE at once
  made hardware failures difficult to isolate.
- **Resolution:** A separate one-shot manual utility now proves status, position,
  and bounded Stop before trusted voice testing. It requires an exact
  target-specific typed phrase, never retries movement, and exits.
- **Verification:** Isolated tests proved 0%, 10%, moving Stop, 100%, and return to
  0% before the voice checklist began.

## Confirmation Safety

- **Risk:** Repeated affirmative speech must be usable, while mixed, denied,
  failed, or unrecognized confirmation must never move the Curtain.
- **Resolution:** Confirmation accepts only affirmative words, explicitly rejects
  any denial or extra wording, allows one recognition attempt, and does not
  connect on cancellation.
- **Verification:** Repeated yes moved exactly once; mixed yes/no, explicit no,
  silence, and out-of-range input left status unchanged.

## Final Validation

- Dedicated Curtain protocol and manual-utility tests: 36 passing.
- Complete non-interactive regression suite: 99 passing.
- Real hardware: status, percentage, Stop, Close, and Open verified.
- Trusted voice: positive and negative confirmation paths verified.
- Git: local configuration remained ignored and no private device identifier was
  committed.
