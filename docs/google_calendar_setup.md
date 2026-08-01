# Google Calendar and Tasks Setup and Testing

## Current Capabilities

CLAP can:

- Read today's schedule.
- Report remaining events and free-time periods.
- Include today's schedule in the daily briefing.
- Parse simple events for today or tomorrow.
- Create an event only after spoken confirmation.
- Preserve Abu Dhabi time with `Asia/Dubai` timestamps.
- Use the Google Calendar account's default reminders.
- Read pending tasks from the default Google Tasks list.
- Read pending tasks due today in `Asia/Dubai`.
- Read pending tasks due tomorrow in `Asia/Dubai`.
- Create a task only after spoken confirmation.

## Local Credential Files

Google OAuth files are stored locally:

```text
config/credentials.json
config/token.json
```

Both paths are excluded by `.gitignore`. Never add their contents to source,
documentation, screenshots, logs, or commits.

The configured OAuth scopes are:

```text
https://www.googleapis.com/auth/calendar.events
https://www.googleapis.com/auth/tasks
```

The Tasks scope is the minimum scope that supports both reading and creating
tasks; the read-only scope cannot create. CLAP detects an existing
Calendar-only token and opens a fresh consent flow. It does not overwrite the
working local token unless the new authorization succeeds.

Enable both the Google Calendar API and Google Tasks API for the Google Cloud
project associated with `credentials.json`.

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
What tasks do I have?
What tasks are due today?
What are my tasks tomorrow?
Read my pending tasks.
```

Test confirmed creation:

```text
Schedule a test event tomorrow at 7:00 p.m.
```

First say `no` and verify nothing is created. Repeat the request, say `yes`,
then verify that Google Calendar shows a one-hour event at 7:00 PM with the
account's default reminder.

Test task creation the same way:

```text
Add buy groceries to my tasks.
Add submit report to my tasks due tomorrow.
```

First say `no` and verify no task is created. Repeat and say `yes`, then verify
the exact title and optional due date in the default Tasks list. Existing tasks
must remain unchanged.

## Automated Tests

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_google_calendar -v
.\.venv\Scripts\python.exe -m unittest tests.test_google_tasks -v
```

The suite covers Calendar parsing, dotted `a.m.`/`p.m.` recognition, timezone
payloads, confirmation behavior, command routing, and daily-briefing intent.
The Tasks suite covers intents, parsing, authorization migration, title and due
date payloads, confirmation, routing, empty results, and failure handling.

## Troubleshooting

- If CLAP reads today's schedule instead of asking for confirmation, inspect
  the `You said:` transcript. The request must contain a recognizable date and
  time.
- If an event appears four hours early, verify the Google Calendar display
  timezone rather than adding a manual offset to CLAP.
- If the browser requests authorization after this upgrade, approve the listed
  Calendar and Tasks permissions. If reauthorization fails, the prior local
  token remains in place; retry without deleting or committing it.
- If Tasks reports that the API is unavailable, confirm the Google Tasks API is
  enabled for the same Google Cloud project.
- If “daily briefing” is transcribed as “daily breathing,” CLAP recognizes the
  common variant.
- If activation immediately enters pause control, restart on the latest code;
  speech-control arming is delayed for three seconds after activation.
