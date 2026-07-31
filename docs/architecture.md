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

While later speech is playing, a physical double clap can request `continue`,
`repeat`, or `stop`.

## External Boundaries

Internet access is required for Google speech recognition, Edge TTS, weather,
forex, news, and Google Calendar. Wake-word detection, local AI generation,
system health, Windows volume control, and desktop automation run locally after
their dependencies are installed.
