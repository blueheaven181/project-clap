# Google Calendar Setup and Testing

## Current Capabilities

CLAP can:

- Read today's schedule.
- Report remaining events and free-time periods.
- Include today's schedule in the daily briefing.
- Parse simple events for today or tomorrow.
- Create an event only after spoken confirmation.
- Preserve Abu Dhabi time with `Asia/Dubai` timestamps.
- Use the Google Calendar account's default reminders.

## Local Credential Files

Google OAuth files are stored locally:

```text
config/credentials.json
config/token.json
```

Both paths are excluded by `.gitignore`. Never add their contents to source,
documentation, screenshots, logs, or commits.

The configured OAuth scope is:

```text
https://www.googleapis.com/auth/calendar.events
```

If the scope changes, the local token may need to be regenerated through the
Google authorization flow.

## Timezone Configuration

CLAP creates events using `Asia/Dubai`. Google Calendar's primary display
timezone must also be `(GMT+04:00) Gulf Standard Time`.

`7:00 PM` Dubai time and `3:00 PM UTC` are the same instant. If the Calendar
interface uses UTC, an otherwise correct event will appear four hours earlier.

## Voice Tests

Start CLAP:

```powershell
.\.venv\Scripts\python.exe .\src\clap_detector.py
```

Test read commands:

```text
What is on my schedule today?
When am I free today?
Am I available today?
```

Test confirmed creation:

```text
Schedule a test event tomorrow at 7:00 p.m.
```

First say `no` and verify nothing is created. Repeat the request, say `yes`,
then verify that Google Calendar shows a one-hour event at 7:00 PM with the
account's default reminder.

## Automated Tests

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_google_calendar -v
```

The suite covers Calendar parsing, dotted `a.m.`/`p.m.` recognition, timezone
payloads, confirmation behavior, command routing, and daily-briefing intent.

## Troubleshooting

- If CLAP reads today's schedule instead of asking for confirmation, inspect
  the `You said:` transcript. The request must contain a recognizable date and
  time.
- If an event appears four hours early, verify the Google Calendar display
  timezone rather than adding a manual offset to CLAP.
- If authorization fails after changing scopes, remove only the local ignored
  token and complete authorization again. Never commit the replacement token.
- If “daily briefing” is transcribed as “daily breathing,” CLAP recognizes the
  common variant.
- If activation immediately enters pause control, restart on the latest code;
  speech-control arming is delayed for three seconds after activation.
