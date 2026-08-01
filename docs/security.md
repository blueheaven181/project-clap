# Project CLAP Security Policy

## Purpose

This document defines the security and privacy rules for Project CLAP.

CLAP will follow a local-first, least-privilege design. New features must remain inside this security boundary.

---

## Core Security Principles

- Keep processing local whenever practical.
- Grant only the permissions required for each feature.
- Never store passwords, API keys, or access tokens in source code.
- Never upload secrets or private information to GitHub.
- Map voice commands to approved functions.
- Never execute unrestricted terminal commands from spoken input.
- Require confirmation before sensitive actions.
- Preserve an emergency stop and manual exit method.
- Treat all external input and API responses as untrusted data.
- Record only the minimum information necessary.

---

## Command Allowlist

CLAP may execute only commands explicitly supported by its command router.

Current approved commands include:

- Daily briefing
- Weather
- System health
- Forex briefing
- AED-to-PHP conversion
- Open TradingView charts
- Launch Spotify
- Control Spotify playback
- Control Windows system volume
- Retrieve categorized news
- Read Google Calendar schedule and availability
- Create Google Calendar events after confirmation
- Read pending Google Tasks
- Create Google Tasks only after confirmation
- Run local articulation-training exercises

Unknown commands must not be converted directly into PowerShell, Python, browser, or operating-system commands.

CLAP should respond:

> Sorry Marc, I do not understand that command yet.

New commands must be reviewed and tested before being added to the allowlist.

---

## Action Risk Levels

### Low Risk

May run without additional confirmation:

- Read weather information
- Read system-health information
- Read forex information
- Calculate currency conversions
- Play a briefing
- Read calendar information
- Read pending task information

### Medium Risk

Should request confirmation when the result affects applications or devices:

- Open applications
- Launch Spotify
- Open trading workspaces
- Control lights
- Control curtains
- Create calendar events or tasks

### High Risk

Must always require explicit confirmation immediately before execution:

- Send an email or message
- Start a voice or video call
- Delete or overwrite files
- Make a purchase
- Place a financial trade
- Unlock a door
- Change security settings
- Share private information
- Execute administrative actions

A conversational response is not authorization. CLAP must ask for clear confirmation.

Example:

> Send this email to the approved recipient. Say “Confirm send” to proceed.

---

## Secrets and Credentials

Secrets must be stored in local environment files or an approved operating-system credential store.

Protected files include:

- `.env`
- `.env.local`
- `config/credentials.json`
- `config/token.json`
- `config/secrets.*`
- Private key files
- Authentication tokens

These files must remain excluded through `.gitignore`.

`.env.example` may be committed only when it contains placeholder names and no real values.

Example:

```text
WEATHER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

Real credentials must never appear in:

- Python source code
- Git commits
- README files
- Screenshots
- Logs
- Error messages
- Test files

If a secret is accidentally exposed, it must be revoked and replaced immediately. Removing it from the latest file is not enough because Git history may still contain it.

---

## Voice and Privacy

- CLAP should listen locally whenever possible.
- Wake-word detection should run locally.
- CLAP must not continuously upload room audio.
- Raw microphone recordings should not be stored by default.
- Temporary recordings must be deleted after processing.
- Private conversations must not be logged.
- CLAP should clearly indicate when it is actively processing speech.
- A manual microphone-disable option must remain available.

---

## AI Safety Boundary

CLAP’s conversational AI may understand, explain, recommend, and prepare actions.

The AI must not directly control the operating system.

The secure command router remains responsible for:

- Checking whether a command is approved
- Validating parameters
- Determining the action risk level
- Requesting confirmation
- Calling the approved Python function
- Rejecting unknown or unsafe requests

Free conversation must never become unrestricted computer control.

---

## Emergency Stop

CLAP must support multiple ways to stop safely:

- Voice command: “CLAP, stop”
- Keyboard interruption: `Ctrl + C`
- Future system-tray Exit button
- Future microphone-disable switch

The global stop command should be capable of stopping:

- Speech playback
- Background music
- The current briefing
- A pending command
- A pending confirmation

The stop command must not perform another action after cancellation.

---

## Email, Messaging, and Calls

Communication actions must use approved contacts.

Before sending or calling, CLAP must state:

- Recipient or contact
- Application or service
- Subject when applicable
- Message summary when applicable
- Action that will occur

CLAP must wait for explicit confirmation.

Speech-recognition confidence alone must never authorize communication with another person.

---

## Mobile Companion Security

A future mobile companion must not expose an unprotected CLAP service to the internet.

Required protections include:

- User authentication
- Encrypted HTTPS communication
- Short-lived access tokens
- Restricted API permissions
- Request validation
- Rate limiting
- Device revocation
- Local-network access by default
- No default router port forwarding

Remote access should use a trusted private-network solution or a carefully secured cloud gateway.

---

## Smart-Home Security

Home Assistant should act as the controlled gateway between CLAP and smart devices.

Recommended protections:

- Place IoT devices on a separate guest or IoT network when practical.
- Do not expose smart devices directly to the internet.
- Use approved device and scene names.
- Require confirmation for security-sensitive devices.
- Keep firmware and Home Assistant updated.
- Maintain a physical method to operate lights and curtains.
- Never allow an AI-generated command to unlock doors automatically.

---

## Logging

Logs should contain only what is required for troubleshooting.

Allowed examples:

- Command category
- Success or failure
- Timestamp
- Module name
- Safe error description

Do not log:

- Passwords
- API keys
- Access tokens
- Full private messages
- Raw microphone audio
- Sensitive conversation transcripts
- Personal health information unless explicitly required and protected

---

## Dependencies

Before adding a Python package:

- Prefer well-maintained packages.
- Verify the official package name.
- Review why the dependency is required.
- Pin or record compatible versions.
- Avoid packages requesting unnecessary permissions.
- Remove unused dependencies.
- Test upgrades before applying them to the working application.

---

## Development Workflow

Before committing:

```text
1. Run syntax checks.
2. Test the affected workflow.
3. Run git diff --check.
4. Review git diff.
5. Stage only the intended files.
6. Review the staged file list.
7. Commit with a clear message.
8. Push to GitHub.
9. Confirm the working tree is clean.
```

Never use broad staging when unrelated private or temporary files may exist.

Prefer staging named files rather than using:

```text
git add .
```

---

## Security Review Checklist

Every new CLAP feature should answer:

- What data does it access?
- Does it require internet access?
- Where is the data stored?
- Is any information sent to a third party?
- What permissions does it require?
- Can it affect another person or device?
- Does it require confirmation?
- Can the user cancel it?
- What happens when it fails?
- Could spoken input trigger an unintended action?
- Are secrets protected from Git?
- Is there a safe manual fallback?

---

## Current Security Status

Project CLAP currently provides:

- Git-based version control
- A protected Python virtual environment
- `.env` exclusion
- Generated-audio exclusion
- Explicit command routing
- Rejection of unknown commands
- Manual `Ctrl + C` interruption
- Incremental testing before commits
- Explicit confirmation before Google Calendar event creation
- Explicit confirmation before Google Tasks creation
- Immediate explicit confirmation before every Curtain 3 movement
- Strict Curtain intent parsing and 0-to-100 position validation
- Ignored local-only storage for the Curtain Bluetooth address
- Fixed official BLE packets in a dedicated module with no local-AI authority
- Git exclusions for Google OAuth credentials and tokens
- Timezone-aware Calendar event payloads
- Shared Google OAuth authorization limited to Calendar events and Tasks
- No permission in the Tasks command surface to alter or delete existing tasks
- A three-second guard between activation and speech-control arming
- Local-AI articulation feedback that must not invent personal facts

Planned security improvements:

- Global “CLAP, stop” command
- Action risk classification
- Confirmation helper for sensitive actions
- Secure configuration loader
- Minimal structured logging
- Dependency review
- Mobile authentication design
- Smart-home network isolation for future networked devices
- Privacy controls for conversational memory

---

## Permanent Rule

CLAP may become intelligent, conversational, and highly capable, but every action must remain controlled, understandable, reversible when possible, and authorized by Marc.
