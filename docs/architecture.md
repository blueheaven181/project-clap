# Architecture

## High-Level Design

```text
Double Clap
    |
    V
Clap Detection Service
    |
    V
CLAP Core Engine
    |
    +---------------------------+
    |            |              |
    V            V              V
Voice Engine Information   Music Player
              Services
                   |
      +------------+------------+
      |            |            |
      V            V            V
   Weather    System Info    Forex
                         Google Calendar
`
```

Google Calendar is a trusted integration. Schedule and availability reads use
the dedicated `google_calendar.py` module. Event writes require explicit spoken
confirmation, include an `Asia/Dubai` timezone, and use the account's default
event reminders.
