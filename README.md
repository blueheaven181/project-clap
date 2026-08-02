# CLAP

## Clap-Activated Personal Assistant

CLAP is a Python-based personal desktop assistant created by Marc Anthony Marquez.

It combines voice activation, trusted automation commands, live information services, local artificial intelligence, desktop control, music playback, and communication coaching.

CLAP is also a practical learning project for Python, software engineering, automation, APIs, artificial intelligence, Git, GitHub, documentation, and troubleshooting.

---

## Current Status

### Version 0.7 — Intelligent Voice Assistant with Google Productivity

CLAP currently supports two activation methods:

- Double clap
- “Hey CLAP” custom wake word

Double-clap activation is currently the more reliable method. Wake-word detection remains under calibration, particularly when speaking farther away from the laptop.

---

## Current Features

### Dual Activation

- Physical double-clap detection
- Custom “Hey CLAP” wake-word model
- Clap sharpness filtering
- Clap cooldown protection
- Activation cooldown protection
- Protection against interpreting “Hey CLAP” as a physical clap
- Three-second speech-control arming delay after activation

### Voice Interaction

- Microsoft neural text-to-speech voice
- Google speech recognition
- Voice-only retry when speech is not understood
- Natural spoken commands
- Follow-up commands without repeating the greeting
- Safe return to standby
- Time-based morning, afternoon, and evening greetings

### Speech and Briefing Control

While CLAP is speaking, only a physical double clap can pause the current
message. Spoken words, including "pause," cannot activate speech pause.

After a physical double clap has paused speech, the following commands are
supported:

- “Continue”
- “Repeat”
- “Stop”

During the daily briefing:

- Continue resumes speech and background music
- Repeat restarts the current spoken section
- Stop cancels the remaining briefing
- Stop prevents trading charts and Spotify prompts from opening
- CLAP returns safely to standby

### Daily Briefing

The complete daily briefing includes:

- Abu Dhabi weather
- Laptop system health
- Forex information
- Today's Google Calendar schedule
- Background briefing music
- Trading workspace automation
- Optional Spotify playback

### Weather

- Current Abu Dhabi weather
- Temperature
- Feels-like temperature
- Humidity
- Wind speed
- Chance of rain
- Daily high and low
- Weather advisories

### System Health

- CPU utilization
- Memory utilization
- Disk utilization
- Health warnings and recommendations

### Forex and Currency Conversion

- EUR/USD
- GBP/USD
- USD/JPY
- AED-to-PHP exchange rate
- Spoken AED amount conversion

Example:

```text
How much is 500 dirhams in pesos?
```

### Live News

CLAP can retrieve and speak current headlines through online news feeds.

Supported categories:

- General news
- Artificial intelligence news
- Technology news
- Cybersecurity news
- Forex news

Example commands:

```text
Latest AI news
Latest technology news
Latest cybersecurity news
Latest forex news
Latest general news
```

### Google Calendar

- Read today's Google Calendar schedule
- Report whether any events remain today
- Report today's remaining free-time periods
- Parse simple event requests for today or tomorrow
- Ask for spoken confirmation before creating an event
- Preserve `Asia/Dubai` event times explicitly
- Use the Google Calendar account's default event reminders
- Include today's schedule in the daily briefing

Example commands:

```text
What is on my schedule today?
When am I free today?
Add workout tomorrow at 7 PM
```

Calendar credentials and authorization tokens are stored locally in
`config/credentials.json` and `config/token.json`. Both files are excluded
from Git.

### Google Tasks

- Read pending tasks from the default Google Tasks list
- Read only pending tasks due today or tomorrow
- Preserve task titles and optional due dates
- Ask for clear spoken confirmation before creating a task
- Never alter, complete, rename, or delete existing tasks
- Interpret spoken task dates using `Asia/Dubai`

Example commands:

```text
What tasks do I have?
What tasks are due today?
What are my tasks tomorrow?
Read my pending tasks.
Add buy groceries to my tasks.
Add submit report to my tasks due tomorrow.
```

Calendar and Tasks share the same ignored local Google credential and token
files. An existing Calendar-only token starts a one-time authorization flow to
add the minimum Tasks scope required for reading and creating tasks.

### SwitchBot Curtain 3

CLAP controls the calibrated Curtain 3 directly over local Bluetooth because
no Hub is installed. It can read position and movement state, then open, close,
stop, or move to a whole-number position from 0% to 100%. Every movement
requires a clear spoken confirmation immediately before execution. Repeated
“yes” is accepted; silence, failed speech, extra wording, or mixed responses
such as “yes yes no” cancel safely.

```text
Open the curtain.
Close the curtains.
What position is the curtain?
Set the curtain to 50 percent.
Stop the curtain.
```

The private Windows Bluetooth address belongs only in the ignored
`config/switchbot.local.json`. Start with `config/switchbot.example.json` and
follow `docs/switchbot_curtain_setup.md`. Never put a real address in source,
tests, documentation, chat, or Git.

The sanitized integration history and final resolution for each encountered
issue are recorded in `docs/switchbot_curtain_issue_log.md`.

The initial real-device checkpoint is complete: isolated and trusted-voice
tests verified status, percentage movement, Stop, full Open, full Close, safe
confirmation cancellation, and no automatic movement retries. iPhone Bluetooth
may remain enabled, but close the SwitchBot device screen before a CLAP command
so the phone does not hold the Curtain's single active BLE connection.

### Trading Workspace Automation

- Opens EUR/USD TradingView chart
- Opens GOLD TradingView chart
- Uses Google Chrome
- Arranges charts across two monitors
- Includes application startup delays and error handling

### Spotify

- Opens Spotify
- Starts playback
- Pauses and resumes playback
- Stops playback
- Skips to the next track
- Returns to the previous track
- Opens configured mood playlists

Example commands:

```text
Play Spotify
Pause music
Resume music
Next track
Previous track
Stop music
Play relaxing music
```

Private Spotify playlist details are stored locally and excluded from GitHub.

### Windows System Volume

- Get the current volume
- Set an exact volume percentage
- Increase volume by a spoken percentage
- Decrease volume by a spoken percentage
- Mute sound
- Unmute sound

Example commands:

```text
Set volume to 50 percent
Reduce volume by 10 percent
Increase volume by 20 percent
Mute the sound
Unmute the sound
```

### Local AI Conversation

CLAP uses Ollama as its local AI engine.

Current local model:

```text
llama3.2:1b
```

Conversation mode can support:

- General conversations
- Communication coaching
- Articulation practice
- Interview practice
- NOC Engineer interview questions
- Azure Administrator interview questions
- Career coaching
- Fitness coaching
- Clear explanations for Python and technical concepts

General questions are sent to the local AI engine. Trusted commands such as weather, system health, currency conversion, Calendar, news, Spotify, and desktop automation remain handled by dedicated CLAP modules.

### Articulation Training

CLAP provides a dedicated voice-guided articulation exercise. Each session:

- Supports work-update, technical-explanation, and achievement-story modes
- Gives one structured professional speaking prompt
- Listens for answers up to 45 seconds and waits for a clear finishing pause
- Scores clarity, conciseness, structure, filler words, and transcript-based
  confidence from 1 to 5
- Identifies one strength
- Focuses on one important improvement
- Suggests a clearer version using only the speaker's facts
- Offers an optional second attempt
- Returns to standby after repeated missed yes-or-no responses
- Accepts stop, cancel, done, or stand by while waiting for an answer
- Does not save transcripts or scores

Example commands:

```text
Start articulation training
Help me improve my articulation
Practice my speaking
Train my communication
Practice a work update
Practice a technical explanation
Practice an achievement story
```

### Private Local Profile

CLAP can load Marc’s personal profile from:

```text
config/marc_profile.local.json
```

The private profile is excluded from GitHub. It allows local personalization without publishing personal information in the repository.

---

## How CLAP Routes Requests

```text
Double Clap or “Hey CLAP”
            |
            v
      “How can I help?”
            |
            v
    Spoken user request
            |
      +-----+------+
      |            |
      v            v
Trusted command   General question
      |            |
      v            v
Dedicated module  Local Ollama AI
```

Examples of trusted commands:

- Weather
- System health
- Forex
- AED-to-PHP conversion
- Live news
- TradingView charts
- Spotify
- Windows system volume
- Daily briefing
- Google Calendar schedule, availability, and confirmed event creation
- Google Tasks reading and confirmed task creation
- SwitchBot Curtain 3 status and confirmed local-Bluetooth movement

Requests that are not recognized as trusted commands can enter local conversation mode.

---

## Main Workflow

```text
Double Clap or “Hey CLAP”
            |
            v
Time-based greeting
            |
            v
“How can I help?”
            |
            v
Command or conversation
            |
            v
Optional follow-up request
            |
            v
Standby
```

Daily briefing workflow:

```text
Activation
    |
    v
Daily briefing request
    |
    v
Background music starts
    |
    v
Weather briefing
    |
    v
System-health briefing
    |
    v
Forex briefing
    |
    v
Calendar schedule
    |
    v
Background music stops
    |
    v
Trading workspace opens
    |
    v
Optional Spotify playback
    |
    v
Standby
```

---

## Project Structure

```text
project-clap
|
|-- assets
|   `-- briefing_music.mp3
|
|-- config
|   |-- marc_profile.local.json
|   `-- spotify_playlists.local.json
|
|-- docs
|   |-- architecture.md
|   |-- articulation_training.md
|   |-- development_notes.md
|   |-- dual_activation_test_checklist.md
|   |-- google_calendar_setup.md
|   |-- local_ai_setup.md
|   |-- project_charter.md
|   |-- requirements.md
|   |-- retrospective_2026-07-27.md
|   |-- retrospective_2026-07-31.md
|   |-- retrospective_2026-08-01.md
|   |-- security.md
|   |-- switchbot_curtain_manual_test_checklist.md
|   |-- switchbot_curtain_issue_log.md
|   |-- switchbot_curtain_setup.md
|   `-- roadmap.md
|
|-- models
|   `-- wake_words
|       |-- hey_Clap.onnx
|       `-- hey_Clap.onnx.data
|
|-- src
|   |-- background_music.py
|   |-- articulation_coach.py
|   |-- clap_detector.py
|   |-- command_router.py
|   |-- conversation.py
|   |-- forex.py
|   |-- google_calendar.py
|   |-- google_auth.py
|   |-- google_tasks.py
|   |-- switchbot_curtain.py
|   |-- switchbot_curtain_discovery.py
|   |-- switchbot_curtain_diagnostic.py
|   |-- switchbot_curtain_manual_test.py
|   |-- single_instance.py
|   |-- greeting.py
|   |-- news.py
|   |-- spotify.py
|   |-- system_health.py
|   |-- system_volume.py
|   |-- voice_commands.py
|   |-- wake_word_test.py
|   |-- weather.py
|   `-- workspace.py
|
|-- tests
|   |-- test_articulation_coach.py
|   |-- test_google_calendar.py
|   |-- test_google_tasks.py
|   |-- test_single_instance.py
|   |-- test_switchbot_curtain.py
|   `-- test_switchbot_curtain_manual.py
|-- .gitignore
|-- CHANGELOG.md
|-- LICENSE
|-- README.md
`-- requirements.txt
```

Local MP3 files, private profile data, credentials, playlist configuration, recordings, and virtual environments are intentionally excluded from GitHub.

---

## Development Environment

CLAP uses Python 3.13 because its microphone dependencies, particularly PyAudio, are compatible with this version.

Create the virtual environment:

```powershell
py -3.13 -m venv .venv
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run CLAP:

```powershell
.\.venv\Scripts\python.exe .\src\clap_detector.py
```

Check Python syntax:

```powershell
.\.venv\Scripts\python.exe -m py_compile .\src\clap_detector.py
```

---

## Internet and Local Services

The following features currently require an internet connection:

- Microsoft neural voice through `edge-tts`
- Google speech recognition
- Weather information
- Forex information
- Live news feeds
- Google Calendar schedule and event operations
- Google Tasks reading and confirmed task creation

The following feature runs locally after its model has been downloaded:

- Ollama conversation engine

SwitchBot Curtain 3 control also runs locally. It requires Windows Bluetooth,
the pinned `bleak` dependency, proximity to the device, and the ignored local
Bluetooth configuration; it does not require internet access.

Desktop automation, local wake-word detection, system health, Windows volume control, and double-clap detection run locally.

---

## Security and Privacy

Project CLAP follows a local-first security approach.

- Secrets and credentials must not be committed to GitHub
- Private profile data remains in local configuration files
- Spotify playlist configuration remains local
- Generated speech files are temporary
- Downloaded briefing music remains local
- Trusted automation commands use dedicated modules
- Local AI does not receive authority to execute arbitrary commands
- External integrations should use minimum required permissions
- Destructive or sensitive actions should require confirmation
- Curtain movements require immediate, unambiguous spoken confirmation

---

## Known Limitations

- “Hey CLAP” may be unreliable at longer distances
- Double clap is currently the preferred activation method
- Google speech recognition requires internet access
- Neural text-to-speech requires internet access
- Voice input currently uses a fixed recording period
- Microphone selection is currently configured for the laptop’s built-in microphone
- Wake-word accuracy depends on microphone quality, distance, and room noise
- Local AI quality and response speed depend on the selected model and computer hardware
- Desktop window automation depends on the current monitor arrangement
- Spotify control currently relies mainly on desktop and media-key automation
- Google Calendar must use the `Asia/Dubai` display timezone. If its display
  timezone is UTC, a correctly stored 7:00 PM Abu Dhabi event appears as
  3:00 PM UTC

---

## Next Priorities

- Test and refine articulation exercise quality and speech recognition
- Improve wake-word reliability
- Refine pause, continue, repeat, and stop behavior
- Add news to the optional daily briefing
- Improve command and conversation routing
- Add smart-lighting scenes
- Build morning, gym, relaxation, and party modes
- Package CLAP as a Windows application
- Evaluate a mobile companion application
- Continue hybrid local and cloud architecture planning

---

## Development Philosophy

CLAP is both a personal assistant and a learning journey.

The project is used to learn:

- Python programming
- Software engineering
- Automation
- Artificial intelligence
- Voice interaction
- API integration
- Desktop integration
- Git and GitHub
- Documentation
- Debugging
- Security
- Project architecture

Development favors small, testable, incremental improvements while preserving working functionality.

---

## Author

Marc Anthony Marquez

NOC Engineer | Azure Administrator | Automation and AI Enthusiast
