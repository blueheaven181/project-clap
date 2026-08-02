# SwitchBot Curtain 3 Manual Hardware Checklist

Interactive hardware tests remain separate from automated tests. Perform them
only with a clear curtain path, a charged motor, and the iPhone app ready as a
fallback. Record results locally without recording the Bluetooth address.

Use `src/switchbot_curtain_manual_test.py` to prove the hardware protocol before
testing the full CLAP voice flow. Its movement mode validates the target,
requires an exact target-specific keyboard phrase, sends only one trusted
command, never retries, and exits.

The `stop-test` action is a separately confirmed two-command sequence: one
validated position command followed by one Stop command after a bounded delay.
Neither command is retried, and Stop is not sent if movement was rejected.

## Isolated Protocol Results

- [x] Read-only diagnostic completed scan, GATT inspection, notification,
  status request, and disconnect successfully.
- [x] No-travel 0% command was accepted while already fully open.
- [x] Requested 10% position was reached and reported exactly.
- [x] Stop was accepted during movement and halted at 32% before the 50% target.
- [x] Full Close reached and reported 100%.
- [x] Full Open reached and reported 0%.
- [x] Each isolated movement required exact target-specific typed confirmation.
- [x] No isolated movement or Stop command was retried automatically.

These checks prove the local BLE protocol independently. Spoken confirmation
and full CLAP routing were tested separately and are recorded below.

## Trusted Voice Results

- [x] Spoken status reported 0% without movement or confirmation.
- [x] Repeated affirmative confirmation authorized exactly one movement.
- [x] Mixed affirmative and negative confirmation cancelled without movement.
- [x] Explicit denial cancelled without movement.
- [x] Failed or unrecognized confirmation cancelled without movement.
- [x] An out-of-range 101% request was rejected before confirmation and BLE.
- [x] Natural Close reached and reported 100%.
- [x] Natural Open reached and reported 0%.
- [x] Natural Stop was confirmed, accepted, and left the stationary Curtain at 0%.
- [x] Every Curtain voice interaction returned directly to wake-word standby.

The isolated and trusted-voice results together complete the applicable initial
real-device validation. Remaining negative-environment cases are covered by the
automated suite or may be repeated manually during future maintenance.

## Repeatable Maintenance Checklist

The unchecked items below are retained as a reusable checklist for future
maintenance or environment changes; they do not indicate that the initial
integration checkpoint is incomplete.

### Safety and Setup

- [ ] No person, pet, or object can be caught in the moving curtain.
- [ ] Curtain 3 remains installed and calibrated in the SwitchBot app.
- [ ] Windows Bluetooth is enabled and within reliable range.
- [ ] `config/switchbot.local.json` exists and is ignored by Git.
- [ ] The real Bluetooth address appears nowhere in tracked files or logs.
- [ ] The SwitchBot app is not holding the Curtain BLE connection.
- [ ] The iPhone app still opens, closes, and stops the curtain manually.

### Read-Only First Test

- [ ] Ask “What position is the curtain?” and confirm no movement occurs.
- [ ] Compare CLAP's reported position with the SwitchBot app.
- [ ] Carefully verify the movement indicator while moving from the app.

### Confirmation Safety

- [ ] “Open the curtain” followed by silence does not move it.
- [ ] Failed or unrecognized speech does not move it.
- [ ] “No,” “cancel,” and “stop” at confirmation do not move it.
- [ ] “Yes yes no” cancels without movement.
- [ ] Unrelated wording containing “yes” does not move it.
- [ ] “Yes yes yes” confirms exactly one movement.

### Movement Commands

- [ ] Confirmed “Open the curtain” moves toward 0% and fully opens.
- [ ] Confirmed “Close the curtain” moves toward 100% and fully closes.
- [ ] Confirmed “Set the curtain to 50 percent” reaches about 50%.
- [ ] Confirmed “Stop the curtain” stops active movement promptly.
- [ ] Values -1%, 101%, and decimals are rejected without movement.

### Failure Handling

- [ ] Missing local config produces a setup message without movement.
- [ ] Disabled Windows Bluetooth produces a safe connection failure.
- [ ] An out-of-range curtain times out promptly.
- [ ] Low-battery, busy, or malformed responses cause no automatic retry.
- [ ] After each failure, the iPhone app still controls the curtain normally.

### Completion

- [ ] Restore ignored local configuration after negative testing.
- [ ] Run the complete automated suite again.
- [ ] Review Git status and staged content for addresses and generated files.
- [ ] Mark roadmap hardware validation complete only after all applicable checks
  pass.
