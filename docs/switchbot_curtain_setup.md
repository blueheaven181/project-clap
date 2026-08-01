# SwitchBot Curtain 3 Local Bluetooth Setup

## Selected Connection

CLAP uses SwitchBot's official local Bluetooth Low Energy protocol because this
installation has no SwitchBot Hub. No SwitchBot account, API token, API secret,
cloud service, or internet connection is required.

## Private Local Information

The only required private value is the Curtain 3 address discovered by Windows
BLE. Do not paste it into chat or place it in source, documentation, tests,
screenshots, issue reports, terminal commands, or commits.

Copy `config/switchbot.example.json` to this ignored file:

```text
config/switchbot.local.json
```

Replace the placeholder locally:

```json
{
  "bluetooth_address": "YOUR_WINDOWS_DISCOVERED_ADDRESS"
}
```

The `config/*.local.json` ignore rule protects this file. Verify it before any
hardware testing:

```powershell
git check-ignore -v config/switchbot.local.json
```

## Windows Preparation

1. Leave the Curtain 3 installed and calibrated in the SwitchBot iPhone app.
2. Close the app's active device screen so it does not hold the BLE connection.
3. Enable Bluetooth on Windows and keep the computer near the curtain.
4. Recreate the virtual environment if a copied environment cannot run, then
   install `requirements.txt` so `bleak` is available.
5. Close the active Curtain screen in the iPhone app, then run the read-only
   local discovery helper:

   ```powershell
   .\.venv\Scripts\python.exe .\src\switchbot_curtain_discovery.py
   ```

6. Put the displayed Windows BLE address only in the ignored file above. On
   Windows this identifier may look like a UUID instead of a traditional MAC
   address; preserve it exactly and do not share it.
7. Run the status command first; it cannot intentionally move the curtain.
   Status is read directly from the Curtain 3 advertisement and does not open a
   GATT connection or send a command packet.

The iPhone app remains the manual fallback if Windows Bluetooth is unavailable.

## Automated Verification

Automated tests use fake BLE clients and sanitized fixed packets. They do not
read local configuration and must never connect to the installed curtain.

## Troubleshooting

Run the read-only GATT diagnostic before retrying a failed movement:

```powershell
.\.venv\Scripts\python.exe .\src\switchbot_curtain_diagnostic.py
```

It scans for only the configured Curtain, connects, checks the required
characteristics and notification subscription, sends only the official
read-only status request, and redacts the private address from errors. It never
sends a movement packet.

- Missing configuration: confirm the exact ignored filename and JSON key.
- Bluetooth unavailable: enable the Windows adapter and confirm OS permission.
- Curtain offline: charge it and move the computer closer.
- No candidate found: the helper recognizes both advertised Curtain names and
  unnamed Curtain 3 service data. Close the app's active Curtain screen, turn
  iPhone Bluetooth off temporarily if necessary, and scan again near the motor.
- Timeout: close the SwitchBot app's device screen, wait briefly, and retry a
  read-only status request once.
- Windows device-not-found error: CLAP resolves the saved address through a
  fresh local scan before every connection. Close the iPhone device screen and
  keep the Windows computer near the motor during that scan.
- Connected but no response: Curtain 3 commands use the protocol's write-without-
  response characteristic mode, then wait up to five seconds for the separate
  notification response.
- Windows disconnect cleanup is limited to three seconds and cannot override a
  successful Curtain response.
- BLE failures report a safe transport phase and redact the configured address,
  allowing diagnosis without logging private device identity.
- CLAP configures its Windows console thread for MTA before importing desktop
  and audio modules, preventing GUI/STA initialization from blocking Bleak
  callbacks.
- Status reads do not require a connection. If status is unavailable while the
  discovery helper sees the Curtain, confirm the saved address exactly matches
  the displayed candidate and retry near the motor.
- Not calibrated: recalibrate only through the SwitchBot app before movement.
- Busy or low battery: do not loop commands; fix the state and issue a new
  spoken request.
