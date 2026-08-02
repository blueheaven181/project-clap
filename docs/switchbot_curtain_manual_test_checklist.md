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

## Safety and Setup

- [ ] No person, pet, or object can be caught in the moving curtain.
- [ ] Curtain 3 remains installed and calibrated in the SwitchBot app.
- [ ] Windows Bluetooth is enabled and within reliable range.
- [ ] `config/switchbot.local.json` exists and is ignored by Git.
- [ ] The real Bluetooth address appears nowhere in tracked files or logs.
- [ ] The SwitchBot app is not holding the Curtain BLE connection.
- [ ] The iPhone app still opens, closes, and stops the curtain manually.

## Read-Only First Test

- [ ] Ask “What position is the curtain?” and confirm no movement occurs.
- [ ] Compare CLAP's reported position with the SwitchBot app.
- [ ] Carefully verify the movement indicator while moving from the app.

## Confirmation Safety

- [ ] “Open the curtain” followed by silence does not move it.
- [ ] Failed or unrecognized speech does not move it.
- [ ] “No,” “cancel,” and “stop” at confirmation do not move it.
- [ ] “Yes yes no” cancels without movement.
- [ ] Unrelated wording containing “yes” does not move it.
- [ ] “Yes yes yes” confirms exactly one movement.

## Movement Commands

- [ ] Confirmed “Open the curtain” moves toward 0% and fully opens.
- [ ] Confirmed “Close the curtain” moves toward 100% and fully closes.
- [ ] Confirmed “Set the curtain to 50 percent” reaches about 50%.
- [ ] Confirmed “Stop the curtain” stops active movement promptly.
- [ ] Values -1%, 101%, and decimals are rejected without movement.

## Failure Handling

- [ ] Missing local config produces a setup message without movement.
- [ ] Disabled Windows Bluetooth produces a safe connection failure.
- [ ] An out-of-range curtain times out promptly.
- [ ] Low-battery, busy, or malformed responses cause no automatic retry.
- [ ] After each failure, the iPhone app still controls the curtain normally.

## Completion

- [ ] Restore ignored local configuration after negative testing.
- [ ] Run the complete automated suite again.
- [ ] Review Git status and staged content for addresses and generated files.
- [ ] Mark roadmap hardware validation complete only after all applicable checks
  pass.
