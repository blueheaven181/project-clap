## Unreleased — Google Calendar Checkpoint

**Date:** 2026-08-01
**Status:** Development Checkpoint

### Added

- Google Calendar schedule commands
- Google Calendar availability and free-time commands
- Simple event-request parsing for today and tomorrow
- Spoken confirmation before Calendar event creation
- Calendar schedule information in the daily briefing
- Default Google Calendar reminders on created events
- Automated Calendar parsing, payload, confirmation, and routing tests

### Fixed

- Calendar routing no longer prevents weather, news, volume, Spotify, and
  other commands later in the command router from running
- Calendar event payloads now reject timezone-less start times and explicitly
  normalize valid start times to `Asia/Dubai`
- Duplicate Calendar imports and unreachable event-query code were removed
- Calendar event requests now accept speech-recognition output using dotted
  `a.m.` and `p.m.` notation

### Tested

- Today's Calendar schedule can be read successfully
- Today's availability and free-time commands work
- Event creation asks for confirmation before writing to Google Calendar
- Affected Python files compile successfully
- `config/credentials.json` and `config/token.json` are ignored and untracked
- Google Calendar's primary display timezone is verified as
  `(GMT+04:00) Gulf Standard Time`

### Timezone Diagnosis

- CLAP sends 7:00 PM Abu Dhabi as `19:00+04:00`, which Google correctly stores
  as the equivalent instant `15:00Z`. A 3:00 PM appearance means the Google
  Calendar web display is using UTC. The account display timezone is now
  verified as Gulf Standard Time (`UTC+04:00`).

---

## Version 0.7 — Intelligent Voice Assistant

**Date:** 2026-07-31
**Status:** Development Milestone

### Added

#### Dual Activation

- Custom “Hey CLAP” OpenWakeWord model
- Local wake-word detection
- Double-clap and wake-word activation in the same listening loop
- Activation cooldown protection
- Wake-word score threshold configuration
- Protection against interpreting “Hey CLAP” as a physical clap
- Dual-activation stability checklist

#### Voice Command Routing

- Central `command_router.py` module
- Weather-only voice command
- System-health-only voice command
- Forex-only voice command
- TradingView voice command
- Spotify voice commands
- System-volume voice commands
- News voice commands
- Unknown-command handling
- Follow-up commands without repeating the greeting

#### Currency Conversion

- Spoken AED amount detection
- AED-to-PHP amount conversion
- Support for questions such as:
  - “How much is 500 dirhams in pesos?”
  - “Convert 100 AED to Philippine pesos”
- Missing-amount handling

#### Local AI Conversation

- Local Ollama integration
- `llama3.2:1b` laptop model
- Reusable `conversation.py` module
- Conversation history
- General conversation mode
- Communication coaching
- Articulation coaching
- Interview practice
- Career coaching
- Fitness coaching
- Conversation exit phrases
- Inactivity checking
- Conversation continuation confirmation
- Routing of general questions to local AI
- Private local user-profile configuration
- Protection against committing private profile data to GitHub

#### Controllable Speech

- Dedicated `pygame` speech channel
- Double-clap interruption while CLAP is speaking
- Pause control
- Continue control
- Repeat control
- Stop control
- Background-music pause and resume synchronization
- Complete briefing cancellation
- Safe return to standby after cancellation

#### Spotify Controls

- Pause Spotify
- Resume Spotify
- Stop Spotify
- Skip to the next track
- Return to the previous track
- Private mood-playlist configuration
- Relaxing-music voice command

#### Windows System Volume

- New `system_volume.py` module
- Read current system volume
- Set an exact volume percentage
- Increase volume by a requested percentage
- Decrease volume by a requested percentage
- Mute system sound
- Unmute system sound

#### Live News

- New `news.py` module
- Online RSS news retrieval
- General news
- Artificial intelligence news
- Technology news
- Cybersecurity news
- Forex news
- Short spoken headline summaries
- Publication-source attribution
- Network and feed-parsing error handling

#### Documentation and Security

- Local AI setup documentation
- Dual-activation test checklist
- Private configuration exclusions
- Credential and secret exclusions
- Expanded `.gitignore` security rules
- Updated README
- Updated roadmap

### Changed

- CLAP now asks “How can I help?” after activation
- Interaction changed from a briefing-only workflow to command-or-conversation routing
- Unrecognized general requests can enter local AI conversation mode
- Trusted automation commands remain handled by dedicated modules
- Voice recognition retries instead of requiring keyboard fallback
- Follow-up commands can run without another activation and greeting
- Speech playback changed from `playsound` to a controllable `pygame` channel
- Double clap now serves as both an activation method and a speech-control signal
- Background music now pauses and resumes with briefing speech
- A stopped briefing no longer continues to system health, forex, charts, or Spotify
- Spotify playback now supports configured moods and media controls
- CLAP can now personalize local AI responses using a private local profile

### Fixed

- Normal speech being incorrectly interpreted as a double clap
- “Hey CLAP” being interpreted as a double clap
- Repeated activation immediately after returning to standby
- “No” incorrectly entering conversation mode
- Voice-recognition failure returning to keyboard input
- Temporary speech files remaining after interrupted sessions
- Background music continuing after the briefing was stopped
- Stopped briefings continuing into later modules
- Speech pause and resume state becoming disconnected from background music
- Spotify command import and indentation errors
- Local AI referring to Marc in the third person
- Local AI claiming to remember information that was not provided
- Multiple Python indentation and control-flow issues found during incremental integration

### Tested

The following workflows were tested successfully:

- Double-clap activation
- “Hey CLAP” activation at close range
- Weather command
- System-health command
- Forex command
- AED-to-PHP amount conversion
- TradingView chart opening and arrangement
- Spotify play, pause, resume, stop, next, and previous controls
- Relaxing Spotify playlist
- Exact and relative Windows volume changes
- Mute and unmute
- Local AI conversation
- Communication and interview coaching
- Private local profile loading
- Conversation exit and standby
- Daily briefing with background music
- Double-clap speech pause
- Continue after pause
- Repeat after pause
- Full briefing stop and return to standby
- General news
- Artificial intelligence news
- Technology news
- Cybersecurity news
- Forex news

### Known Limitations

- “Hey CLAP” is less reliable at longer distances
- Double clap remains the preferred activation method
- The custom wake-word model requires further training
- Voice recognition currently requires an internet connection
- Neural text-to-speech currently requires an internet connection
- Weather, forex, and news require internet access
- Voice input still uses a fixed recording duration
- Microphone selection is currently fixed for the laptop
- Direct voice interruption during loud speech or music is unreliable
- Double clap is currently used before spoken pause controls
- Local AI speed and quality are limited by laptop hardware
- The `llama3.2:1b` model may occasionally produce weak or inaccurate answers
- Spotify control relies mainly on desktop automation and media keys
- News feeds may contain duplicate, low-quality, or loosely related headlines
- Two experimental interruption test files remain under local review

---
