# Project CLAP Roadmap

## Project Direction

CLAP is evolving from a clap-activated daily briefing tool into a hybrid personal assistant that combines:

- Trusted automation commands
- Voice interaction
- Local artificial intelligence
- Live information services
- Desktop automation
- Smart-room control
- Communication and career coaching

Development follows small, testable increments while preserving working functionality.

---

## Sprint 0 — Foundation

Status: Completed

- [x] Create GitHub repository
- [x] Establish project structure
- [x] Create initial documentation
- [x] Document architecture and requirements
- [x] Configure the development environment

---

## Sprint 1 — First Contact

Status: Completed

- [x] Install Python
- [x] Configure VS Code
- [x] Configure Git and GitHub
- [x] Create the first Python application
- [x] Produce the first neural voice greeting

---

## Sprint 1.2 — Reusable Voice Engine

Status: Completed

Objective: Create a reusable voice engine for all CLAP modules.

- [x] Create `greeting.py`
- [x] Move neural voice generation into a reusable function
- [x] Create the `speak()` function
- [x] Test voice output
- [x] Integrate the voice engine with CLAP
- [x] Add temporary speech-file cleanup
- [x] Move speech playback to a dedicated `pygame` channel
- [x] Add pause, resume, repeat, and stop support

---

## Sprint 1.3 — Double-Clap Detection

Status: Completed

Objective: Activate and control CLAP through physical claps.

- [x] Install and configure `sounddevice`
- [x] Detect microphone input
- [x] Detect two claps within a configured window
- [x] Trigger CLAP activation
- [x] Add clap cooldown protection
- [x] Add clap sharpness filtering
- [x] Reduce activation from normal speech
- [x] Use double clap as a reliable speech-interruption signal

---

## Sprint 2.0 — Intelligent Greeting

Status: Completed

- [x] Detect the current time
- [x] Determine morning, afternoon, or evening
- [x] Integrate time-based greetings
- [x] Use the greeting during clap and wake-word activation

---

## Sprint 2.1 — Weather Briefing

Status: Completed

- [x] Create `weather.py`
- [x] Retrieve live Abu Dhabi weather
- [x] Report temperature and feels-like temperature
- [x] Report humidity and wind speed
- [x] Report chance of rain
- [x] Report daily high and low
- [x] Provide weather advisories
- [x] Add API error handling
- [x] Integrate weather with voice output
- [x] Integrate weather with the daily briefing
- [x] Add a weather-only voice command

---

## Sprint 2.2 — System Health Briefing

Status: Completed

- [x] Create `system_health.py`
- [x] Report CPU utilization
- [x] Report memory utilization
- [x] Report disk utilization
- [x] Provide health warnings
- [x] Integrate system health with voice output
- [x] Add a system-health-only voice command

---

## Sprint 2.3 — Forex and Currency Conversion

Status: Completed

- [x] Create `forex.py`
- [x] Report EUR/USD
- [x] Report GBP/USD
- [x] Report USD/JPY
- [x] Report the AED-to-PHP rate
- [x] Detect spoken currency amounts
- [x] Convert a requested AED amount to PHP
- [x] Handle missing amounts
- [x] Add API error handling
- [x] Add forex-only voice commands

Example:

```text
How much is 500 dirhams in pesos?
```

---

## Sprint 2.4 — Trading Workspace Automation

Status: Completed

- [x] Open the EUR/USD TradingView chart
- [x] Open the GOLD TradingView chart
- [x] Discover actual window coordinates
- [x] Support a dual-monitor workspace
- [x] Add application startup delays
- [x] Arrange trading windows automatically
- [x] Add workspace error handling
- [x] Add a TradingView voice command

---

## Sprint 2.5 — Spotify Integration

Status: Completed

- [x] Create `spotify.py`
- [x] Launch Spotify
- [x] Start playback
- [x] Pause playback
- [x] Resume playback
- [x] Stop playback
- [x] Skip to the next track
- [x] Return to the previous track
- [x] Add mood-playlist configuration
- [x] Keep private playlist details outside GitHub
- [x] Add relaxing-music playback
- [x] Add Spotify commands to the command router

Future improvements:

- [ ] Integrate the official Spotify Web API
- [ ] Search for artists, albums, and playlists by voice
- [ ] Select a playback device
- [ ] Read the currently playing track
- [ ] Improve playback-state awareness

---

## Sprint 3.0 — Hands-Free Voice Interaction

Status: Completed

- [x] Create `voice_commands.py`
- [x] Install SpeechRecognition and PyAudio
- [x] Configure Python 3.13 for PyAudio compatibility
- [x] Select the built-in laptop microphone
- [x] Add ambient-noise calibration
- [x] Add fixed-duration voice recording
- [x] Recognize natural spoken responses
- [x] Add microphone and recognition error handling
- [x] Replace keyboard fallback with voice-only retry
- [x] Continue listening until a response is understood
- [x] Add follow-up voice commands
- [x] Return safely to standby after “no” or “stop”

Future improvements:

- [ ] Move microphone selection into configuration
- [ ] Replace fixed-duration recording with smarter listening
- [ ] Evaluate offline speech recognition
- [ ] Improve recognition while music or speech is playing

---

## Sprint 3.1 — Background Briefing Music

Status: Completed

- [x] Create `background_music.py`
- [x] Install and configure `pygame`
- [x] Start music before spoken reports
- [x] Loop music during the briefing
- [x] Control background-music volume
- [x] Stop music safely with `finally`
- [x] Pause music during speech interruption
- [x] Resume music with continued speech
- [x] Stop music when the briefing is cancelled
- [x] Exclude the local MP3 from GitHub

---

## Sprint 3.2 — Documentation and Reproducibility

Status: In Progress

- [x] Create `requirements.txt`
- [x] Document the Python 3.13 environment
- [x] Create development notes
- [x] Create a dual-activation test checklist
- [x] Document local AI setup
- [x] Create the Version 0.6 retrospective
- [x] Update the README for Version 0.7
- [x] Update the roadmap for Version 0.7
- [ ] Update the changelog for Version 0.7
- [ ] Create the Version 0.7 sprint retrospective
- [ ] Review project architecture documentation
- [ ] Review requirements documentation
- [ ] Decide whether experimental test files should be retained
- [ ] Confirm a clean Git working tree

---

## Sprint 4.0 — Voice Command Routing

Status: Completed

Objective: Route trusted commands to dedicated CLAP modules.

- [x] Ask “How can I help?” after activation
- [x] Create `command_router.py`
- [x] Add weather command
- [x] Add system-health command
- [x] Add forex command
- [x] Add AED-to-PHP conversion command
- [x] Add daily-briefing routing
- [x] Add TradingView command
- [x] Add Spotify commands
- [x] Add system-volume commands
- [x] Add news commands
- [x] Add unknown-command handling
- [x] Preserve existing modules
- [x] Route general questions to local AI conversation

---

## Sprint 4.1 — Dual Activation

Status: Completed with Ongoing Calibration

Objective: Support both physical and spoken activation.

- [x] Preserve double-clap activation
- [x] Install OpenWakeWord
- [x] Test the reference “Hey Jarvis” model
- [x] Train a custom “Hey CLAP” model
- [x] Add the custom model to the repository
- [x] Integrate wake-word detection with CLAP
- [x] Prevent wake-word speech from being interpreted as claps
- [x] Add activation cooldown protection
- [x] Create a dual-activation test checklist
- [x] Test normal speech against false clap activation
- [x] Keep double clap as the reliable primary method

Ongoing improvements:

- [ ] Improve “Hey CLAP” recognition at longer distances
- [ ] Collect additional positive and negative training samples
- [ ] Retrain the wake-word model with improved recall
- [ ] Test with an external microphone
- [ ] Measure false activations during longer listening sessions

---

## Sprint 4.2 — Controllable Speech and Briefing Interruption

Status: Completed

Objective: Let Marc pause and control CLAP while it is speaking.

- [x] Use a dedicated speech playback channel
- [x] Detect a double clap during speech
- [x] Pause active speech
- [x] Pause background music
- [x] Accept “continue”
- [x] Accept “repeat”
- [x] Accept “stop”
- [x] Resume background music after continue
- [x] Restart the current speech after repeat
- [x] Cancel the remaining daily briefing after stop
- [x] Skip charts and Spotify after cancellation
- [x] Return safely to standby

Future improvements:

- [ ] Improve direct voice barge-in without requiring a double clap
- [ ] Add reliable hands-free pause detection
- [ ] Prevent speaker echo from reaching the speech recognizer
- [ ] Evaluate microphone echo cancellation
- [ ] Add interruption tests for conversation and news modes

---

## Sprint 4.3 — Local AI Conversation

Status: Completed for Initial Implementation

Objective: Give CLAP a local conversational engine while keeping automation controlled.

- [x] Install Ollama
- [x] Select `llama3.2:1b` for laptop performance
- [x] Create `conversation.py`
- [x] Add conversation history
- [x] Add communication coaching
- [x] Add articulation coaching
- [x] Add interview practice
- [x] Add career coaching
- [x] Add fitness coaching
- [x] Add conversation exit phrases
- [x] Add inactive-user checking
- [x] Ask whether the conversation should continue
- [x] Route unrecognized general requests to local AI
- [x] Keep trusted commands outside the AI engine
- [x] Add a private local profile
- [x] Exclude private profile data from GitHub

Future improvements:

- [ ] Improve answer quality with a stronger desktop model
- [ ] Add controlled long-term memory
- [ ] Add conversation summaries
- [ ] Add topic and coaching modes
- [ ] Add optional cloud AI fallback
- [ ] Add source-based retrieval for trusted documents
- [ ] Improve response speed and streaming speech

---

## Sprint 4.4 — Windows System Volume

Status: Completed

- [x] Install `pycaw`
- [x] Create `system_volume.py`
- [x] Read the current Windows volume
- [x] Set an exact volume percentage
- [x] Increase volume
- [x] Decrease volume
- [x] Mute audio
- [x] Unmute audio
- [x] Add voice-command routing
- [x] Test all volume commands

---

## Sprint 4.5 — Live News Briefings

Status: Completed for Initial Implementation

Objective: Provide short, sourced, current news headlines.

- [x] Create `news.py`
- [x] Retrieve online RSS news feeds
- [x] Add general news
- [x] Add artificial intelligence news
- [x] Add technology news
- [x] Add cybersecurity news
- [x] Add forex news
- [x] Limit the number of spoken headlines
- [x] Include publication sources
- [x] Add network and parsing error handling
- [x] Add voice-command routing
- [x] Complete end-to-end voice testing

Future improvements:

- [ ] Add news to the optional daily briefing
- [ ] Add source allowlists
- [ ] Remove duplicate or low-quality headlines
- [ ] Add publication time filtering
- [ ] Allow category and headline-count preferences
- [ ] Let Marc request more details about one headline

---

## Sprint 5.0 — Smart Curtain Integration

Status: Next Hardware Sprint

Objective: Control SwitchBot Curtain 3 through CLAP.

Planned work:

- [ ] Install and configure SwitchBot Curtain 3
- [ ] Test control through the SwitchBot mobile application
- [ ] Confirm the available Bluetooth interface
- [ ] Research the supported local Bluetooth protocol
- [ ] Create a separate curtain-control test module
- [ ] Add open-curtain command
- [ ] Add close-curtain command
- [ ] Add curtain-position command
- [ ] Add timeout and connection error handling
- [ ] Add confirmation before risky movement if required
- [ ] Integrate curtain commands with `command_router.py`
- [ ] Test without breaking existing CLAP modules

Example commands:

```text
Open the curtain
Close the curtain
Set the curtain to 50 percent
```

---

## Sprint 5.1 — Smart Lighting and Room Modes

Status: Planned

- [ ] Select a locally controllable smart bulb
- [ ] Select a locally controllable light strip
- [ ] Add light power controls
- [ ] Add brightness controls
- [ ] Add color controls
- [ ] Add room scenes
- [ ] Create gym mode
- [ ] Create relaxation mode
- [ ] Create sleep mode
- [ ] Create party mode
- [ ] Create morning mode
- [ ] Coordinate curtain, lighting, Spotify, and volume

---

## Sprint 5.2 — Google Productivity Integration

Status: In Progress

- [x] Integrate Google Calendar schedule reading
- [ ] Integrate Google Tasks
- [x] Use a Calendar event scope that supports reading and event creation
- [x] Store credentials outside GitHub
- [x] Read today’s calendar
- [x] Report today's remaining schedule and availability
- [x] Ask for confirmation before creating calendar events
- [ ] Fix event-creation timezone handling; a 7:00 PM request may display at
  3:00 PM in Google Calendar
- [ ] Read pending tasks
- [ ] Create tasks with confirmation
- [ ] Add calendar information to the daily briefing
- [ ] Add reminder workflows

---

## Sprint 5.3 — Communication and Career Coach

Status: Planned Expansion

- [ ] Add dedicated articulation exercises
- [ ] Add structured mock interviews
- [ ] Add NOC Engineer interview mode
- [ ] Add Azure Administrator interview mode
- [ ] Score clarity, structure, and confidence
- [ ] Suggest improved answers
- [ ] Track recurring communication improvements locally
- [ ] Keep personal coaching records private

---

## Sprint 5.4 — Fitness and VITAL Integration

Status: Future

- [ ] Define a secure interface between CLAP and VITAL
- [ ] Read local fitness summaries
- [ ] Provide general fitness coaching
- [ ] Track steps, workouts, runs, and weight trends
- [ ] Add approximate meal and macro estimation
- [ ] Keep health information private
- [ ] Clearly separate general coaching from medical advice

---

## Sprint 6.0 — Packaging and Startup

Status: Planned

- [ ] Refactor startup into a clean application entry point
- [ ] Move configuration out of source code
- [ ] Add structured logging
- [ ] Add automated tests
- [ ] Package CLAP as a Windows executable
- [ ] Evaluate an MSI installer
- [ ] Add safe Windows startup behavior
- [ ] Add a system-tray status indicator
- [ ] Add microphone and service status checks
- [ ] Document installation and recovery

---

## Sprint 6.1 — Mobile Companion

Status: Future

- [ ] Define a secure local API
- [ ] Create authenticated communication
- [ ] Show CLAP status on a phone
- [ ] Send commands from a phone
- [ ] Receive briefing summaries
- [ ] Add remote notification support
- [ ] Avoid exposing CLAP directly to the public internet

---

## Containerization and Hybrid Architecture

Status: Future

Objective: Preserve Windows hardware control while separating suitable services.

- [ ] Keep microphone, speaker, wake word, and desktop automation on Windows
- [ ] Separate service modules from desktop-control modules
- [ ] Create a Python 3.13 container image
- [ ] Containerize suitable weather, forex, and news services
- [ ] Add a controlled API between desktop CLAP and services
- [ ] Evaluate Azure Container Apps
- [ ] Document local, containerized, and cloud deployment options
- [ ] Preserve local operation if cloud services are unavailable

---

## Security Principles

Every future sprint must follow these rules:

- Keep credentials and private data outside GitHub
- Grant external services only the permissions they require
- Keep trusted commands in dedicated modules
- Do not let the AI engine execute arbitrary system commands
- Require confirmation for sensitive or destructive actions
- Validate external data before using it
- Handle network failures safely
- Preserve a local standby mode
- Add logs without storing unnecessary private speech
- Test new integrations independently before production integration

---

## Milestones

### 2026-07-12 — Version 0.1: First Contact

- Project structure
- Neural voice greeting
- Double-clap activation
- GitHub repository

### 2026-07-28 — Version 0.6: Hands-Free Briefing

- Spoken briefing confirmation
- Spoken Spotify confirmation
- Background briefing music
- Python 3.13 environment
- Reproducible dependency installation

### 2026-07-31 — Version 0.7: Intelligent Voice Assistant

Current development milestone:

- Dual activation
- Voice command routing
- Currency amount conversion
- Local AI conversation
- Private personalization
- Spotify controls and mood playback
- System-volume control
- Controllable speech interruption
- Live categorized news
- Expanded security boundaries
