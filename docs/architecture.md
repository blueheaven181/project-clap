# Project CLAP Architecture

## High-Level Design

```text
Double clap or "Hey CLAP"
            |
            v
   Activation detector
            |
            v
  Voice command capture
            |
            v
     Intent routing
      /          \
     v            v
Trusted command  General conversation
     |            |
     v            v
Dedicated module Local Ollama model
```

## Trusted Command Modules

The command router sends approved requests to dedicated modules:

- `weather.py` retrieves Abu Dhabi weather.
- `system_health.py` reports laptop health.
- `forex.py` retrieves exchange rates and opens trading charts.
- `google_calendar.py` reads schedules and creates confirmed events.
- `google_auth.py` manages the shared least-privilege Calendar and Tasks OAuth
  token, including consent when a local token lacks the Tasks scope.
- `google_tasks.py` reads pending tasks and creates new confirmed tasks in the
  default task list.
- `switchbot_curtain.py` validates and executes a fixed set of official Curtain
  3 BLE packets. It cannot execute arbitrary device data.
- `news.py` retrieves and summarizes categorized news.
- `spotify.py` controls playback and configured mood playlists.
- `system_volume.py` controls Windows audio.
- `workspace.py` arranges desktop windows.
- `articulation_coach.py` runs structured speaking exercises and requests
  constrained feedback from the local Ollama conversation engine.

Unknown general requests may enter `conversation.py`. The local AI does not
receive authority to execute arbitrary operating-system commands.

## Google Calendar Flow

```text
Spoken event request
        |
        v
Parse date and time in Asia/Dubai
        |
        v
Speak event details and request confirmation
        |
     +--+--+
     |     |
    Yes    No
     |     |
     v     v
Google API Cancel safely
```

Calendar credentials are loaded from ignored local files. Event payloads are
timezone-aware, use `Asia/Dubai`, and inherit the Google Calendar account's
default reminder settings. The account display timezone is also configured for
Gulf Standard Time (`UTC+04:00`).

## Google Tasks Flow

```text
Spoken Tasks request
        |
   +----+----+
   |         |
  Read      Create request
   |         |
   v         v
Pending   Parse title and optional Dubai date
tasks             |
                  v
           Speak details and confirm
               +--+--+
               |     |
              Yes    No or failed speech
               |     |
               v     v
          Insert new  Cancel safely
             task
```

Tasks uses `@default`, excludes completed and deleted tasks, and never calls
update, delete, or completion methods. Task due dates are date-only Google
Tasks values; spoken `today` and `tomorrow` read filters and creation dates are
resolved in `Asia/Dubai`.

## SwitchBot Curtain Flow

```text
Spoken curtain request
        |
        v
Strict intent parsing and position validation
        |
   +----+----+
   |         |
 Status    Movement
   |         |
   v         v
BLE read   Speak exact action and confirm
                  |
             +----+----+
             |         |
         Clear yes   Anything else
             |         |
             v         v
       Fixed BLE packet  Cancel without connecting
```

The router passes only status, open, close, set-position, and stop operations
to the dedicated module. The module uses the official Curtain 3 BLE service,
waits briefly for an explicit response, and never retries movement
automatically. The ignored `config/switchbot.local.json` contains the private
Windows Bluetooth address. General Ollama conversation has no path to this BLE
client or its raw packets.

## Articulation Training Flow

```text
Training request -> Speaking prompt -> Spoken answer -> Local AI feedback
                                                     -> Optional retry
```

The coach focuses on one strength and one improvement per exercise. Its clearer
sample answer must use only information present in the user's response.

## Daily Briefing Flow

The daily briefing speaks weather, system health, forex, and today's Calendar
schedule while background music is active. If speech control returns `stop`,
the remaining briefing, trading workspace, and Spotify prompt are skipped.

## Activation and Speech Control

Wake-word inference runs locally through OpenWakeWord. Double clap remains the
most reliable activation method. After either activation method, speech-control
claps are ignored for three seconds so activation audio cannot immediately
pause the greeting.

While later speech is playing, only a validated physical double clap may pause
the message. Voice activity and spoken commands cannot request pause. After the
double-clap pause, CLAP listens for `continue`, `repeat`, or `stop`.

## External Boundaries

Internet access is required for Google speech recognition, Edge TTS, weather,
forex, news, Google Calendar, and Google Tasks. Wake-word detection, local AI generation,
system health, Windows volume control, desktop automation, and SwitchBot Curtain
3 BLE control run locally after their dependencies are installed.
