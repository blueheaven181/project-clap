## Unreleased — Google Tasks Checkpoint

**Date:** 2026-08-01
**Status:** Development Checkpoint

### Added

- Initial SwitchBot Curtain 3 integration using the official local Bluetooth
  protocol, with no Hub or cloud credentials required
- Dedicated Curtain module for status, open, close, position, and stop commands
- Strict trusted Curtain intents, position validation, bounded BLE timeouts, and
  graceful configuration, offline, device, and malformed-response failures
- Immediate movement confirmation that accepts repeated yes responses and
  cancels mixed, contradictory, failed, or unrecognized speech
- Ignored local Bluetooth configuration, sanitized example, setup guide,
  hardware checklist, and focused automated tests
- Read-only local Curtain discovery helper that keeps the Windows BLE address
  in the user's terminal and ignored configuration
- Curtain discovery recognizes unnamed Curtain 3 advertisements through the
  official SwitchBot service-data device type
- Windows BLE connections resolve the configured address to a freshly scanned
  device object before connecting, avoiding stale-cache device-not-found errors
- Curtain BLE packets use write-without-response mode before waiting for the
  device's separate notification, preventing GATT acknowledgement stalls
- Curtain status reads use the official connection-free advertisement fields
  for calibration, battery, movement, and raw 0-open to 100-closed position

- Google Tasks pending-task reading from the default task list
- Due-today task filtering using the `Asia/Dubai` date
- Confirmed task creation with exact titles and optional due dates
- Shared Calendar and Tasks OAuth authorization with safe scope migration
- Focused Tasks intent, parsing, payload, API, routing, empty-result, and
  failure-handling tests
- Selectable work-update, technical-explanation, and achievement-story
  articulation modes
- Explicit 1-to-5 articulation scores for clarity, conciseness, structure,
  filler words, and transcript-based confidence
- Deterministic filler-word counting and common speech-recognition variant
  handling for articulation commands
- Privacy-safe articulation logging that does not print answer transcripts
- Expanded articulation intent, scoring, mode-routing, and session tests
- Dedicated voice-guided articulation training
- Structured professional speaking exercises with concise AI feedback
- Optional retry after receiving an improved answer
- Articulation intent, routing, feedback-prompt, and session tests
- Google Calendar schedule commands
- Google Calendar availability and free-time commands
- Simple event-request parsing for today and tomorrow
- Spoken confirmation before Calendar event creation
- Calendar schedule information in the daily briefing
- Default Google Calendar reminders on created events
- Automated Calendar parsing, payload, confirmation, and routing tests
- Dedicated Google Calendar setup, testing, and troubleshooting guide

### Fixed

- Conversation mode now exits immediately for natural or repeated stop phrases
  such as "stop now" and "stop stop stop" instead of continuing to listen
- Mixed task-creation responses such as "yes yes no" now cancel safely instead
  of being treated as confirmation
- Tomorrow Tasks requests now filter to tomorrow's Dubai due date instead of
  returning every pending task
- Due-today Tasks routing now recognizes natural speech variants including
  "do I have task today" and "what are my task today"
- Google Tasks read intent now accepts singular speech transcripts such as
  "what task do I have" as well as plural variants
- Local conversation responses now address Marc directly as "you" instead of
  describing him in the third person
- Google Tasks read requests now pass the activation loop's trusted-command
  gate instead of incorrectly starting local conversation mode
- Existing Calendar-only tokens now request fresh consent when the Tasks scope
  is missing instead of attempting a refresh that cannot add permissions
- Failed or unrecognized task confirmations cancel creation safely
- The speech layer now accepts pause requests only from the validated physical
  double-clap trigger; speech and voice-command triggers are explicitly rejected
- Speech-control pause now requires two sharper, distinctly timed clap
  transients so CLAP's voice and the user's speech do not activate pause
- A paused message automatically continues after three unrecognized
  speech-control responses instead of remaining in a listening loop
- Articulation answers now use silence-ended listening with a 45-second limit
  instead of being cut off after a fixed five-second recording
- Voice sensitivity now adapts after ambient-noise calibration rather than
  forcing a high fixed microphone threshold
- Articulation yes-or-no prompts and command follow-ups now return to standby
  after three missed responses instead of retrying indefinitely
- Stop and standby phrases cancel articulation training without being scored as
  an exercise answer
- Duplicate `requests` import and private-profile loading in the conversation
  module were removed
- Calendar routing no longer prevents weather, news, volume, Spotify, and
  other commands later in the command router from running
- Calendar event payloads now reject timezone-less start times and explicitly
  normalize valid start times to `Asia/Dubai`
- Duplicate Calendar imports and unreachable event-query code were removed
- Calendar event requests now accept speech-recognition output using dotted
  `a.m.` and `p.m.` notation
- Daily briefing intent is detected before direct-command routing, uses
  case-insensitive transcripts, and accepts the common `daily breathing`
  recognition variant
- Wake-word and double-clap activation now delay speech-control arming for
  three seconds, preventing activation audio from immediately pausing CLAP's
  greeting
- Active project documentation now reflects the Calendar integration,
  briefing routing, security boundary, architecture, and current roadmap

### Tested

- The focused Curtain suite passes all 24 simulated-hardware tests without
  connecting to or moving a real device
- Python compilation and all 84 non-interactive automated regression tests pass;
  manual microphone and Curtain hardware checks remain separate

- The focused Google Tasks and Calendar suites pass all 26 tests
- The complete automated regression suite passes all 48 tests; interactive
  microphone diagnostics remain separate manual tests
- Double-clap-only pause policy passes three focused authorization tests
- The focused voice and articulation suites pass all 17 tests
- The full regression suite passes all 31 tests
- All affected articulation Python files compile successfully
- The 13-test articulation suite and 24-test full regression suite pass
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
