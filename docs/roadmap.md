# Project CLAP Roadmap

## Sprint 0 — Foundation ✅

Status: Completed

- [x] Create GitHub repository
- [x] Establish project structure
- [x] Create initial documentation
- [x] Document architecture and requirements
- [x] Configure the development environment

---

## Sprint 1 — First Contact ✅

Status: Completed

- [x] Install Python
- [x] Configure VS Code
- [x] Configure Git and GitHub
- [x] Create the first Python application
- [x] Produce the first voice greeting

---

## Sprint 1.2 — Reusable Voice Engine ✅

Status: Completed

Objective: Create a reusable voice engine for all CLAP modules.

- [x] Create `greeting.py`
- [x] Move the neural voice into a reusable function
- [x] Create the `speak()` function
- [x] Test voice output
- [x] Integrate the voice engine with `main.py`

Success criteria: CLAP can produce a neural spoken greeting from any module.

---

## Sprint 1.3 — Double-Clap Detection ✅

Status: Completed

Objective: Activate CLAP through a double clap.

- [x] Install and configure `sounddevice`
- [x] Detect microphone input
- [x] Detect two claps within a configured window
- [x] Trigger the voice greeting
- [x] Add clap cooldown protection
- [x] Test activation reliability

Success criteria: Two claps activate CLAP without repeated false triggers.

---

## Sprint 2.0 — Intelligent Greeting ✅

Status: Completed

Objective: Deliver the correct greeting based on the current time.

- [x] Detect the current time
- [x] Determine morning, afternoon, or evening
- [x] Integrate the greeting with `greeting.py`
- [x] Update clap activation

---

## Sprint 2.0.1 — Stability Improvements ✅

Status: Completed

- [x] Fix startup greeting behavior
- [x] Fix time-based greeting selection
- [x] Calibrate the clap threshold
- [x] Add clap cooldown protection
- [x] Reduce false clap detections
- [x] Clean up generated audio files
- [x] Exclude generated MP3 files from Git

---

## Sprint 2.1 — Weather Briefing ✅

Status: Completed

Objective: Provide live weather information for Abu Dhabi.

- [x] Create `weather.py`
- [x] Retrieve live weather data
- [x] Report temperature and feels-like temperature
- [x] Report humidity and wind speed
- [x] Report chance of rain
- [x] Provide weather advisories
- [x] Integrate weather with the voice engine
- [x] Integrate weather with the daily briefing
- [x] Add API error handling

---

## Sprint 2.2 — System Health Briefing ✅


Status: Completed

Objective: Provide useful laptop health information.

- [x] Create `system_health.py`
- [x] Report CPU utilization
- [x] Report memory utilization
- [x] Report disk utilization
- [x] Provide health warnings and recommendations
- [x] Integrate system health with the voice engine

---

## Sprint 2.3 — Forex Briefing ✅

Status: Completed

Objective: Provide current market and currency information.

- [x] Create `forex.py`
- [x] Report EUR/USD
- [x] Report GBP/USD
- [x] Report USD/JPY
- [x] Report AED-to-PHP conversion
- [x] Add external API error handling
- [x] Integrate forex with the daily briefing

---

## Sprint 2.4 — Trading Workspace Automation ✅

Status: Completed

Objective: Automatically prepare the trading workspace.

- [x] Open the EUR/USD TradingView chart
- [x] Open the GOLD TradingView chart
- [x] Discover actual window coordinates
- [x] Support a dual-monitor workspace
- [x] Add application startup delays
- [x] Arrange trading windows automatically
- [x] Add workspace error handling

---

## Sprint 2.5 — Spotify Integration ✅

Status: Completed

Objective: Launch Spotify and start playback after the briefing.

- [x] Create `spotify.py`
- [x] Ask for confirmation before launching Spotify
- [x] Launch Spotify
- [x] Send the play command
- [x] Preserve the option to keep Spotify closed

---

## Sprint 3.0 — Hands-Free Briefing ✅

Status: Completed

Objective: Replace typed confirmations with spoken responses.

- [x] Create `voice_commands.py`
- [x] Install SpeechRecognition and PyAudio
- [x] Configure Python 3.13 for PyAudio compatibility
- [x] Create a Python 3.13 virtual environment
- [x] Select the laptop microphone
- [x] Add ambient-noise handling
- [x] Add fixed-duration voice recording
- [x] Recognize natural Yes/No phrases
- [x] Preserve keyboard input as a fallback
- [x] Add recognition and microphone error handling
- [x] Add spoken confirmation for the daily briefing
- [x] Add spoken confirmation for Spotify

Success criteria: CLAP accepts spoken Yes/No responses while preserving keyboard fallback.

---

## Sprint 3.1 — Background Briefing Music ✅

Status: Completed

Objective: Play quiet background music while CLAP delivers the briefing.

- [x] Download a licensed local instrumental MP3
- [x] Create `background_music.py`
- [x] Install and configure `pygame`
- [x] Start background music before spoken reports
- [x] Play music at a controlled volume
- [x] Loop music during the briefing
- [x] Stop music after the briefing
- [x] Use `finally` to stop music safely after errors
- [x] Exclude the local MP3 from Git

---

## Sprint 3.2 — Documentation and Reproducibility 🚧

Status: In Progress

- [x] Create `requirements.txt`
- [x] Document the Python 3.13 environment
- [x] Update the main README for v0.6
- [x] Update the project roadmap
- [ ] Update the changelog
- [ ] Complete the sprint retrospective
- [ ] Confirm a clean Git working tree

---

## Sprint 4.0 — Voice Command Routing 📋

Status: Planned

Objective: Allow CLAP to run individual features through natural voice commands.

- [ ] Ask “How can I help?” after activation
- [ ] Create `command_router.py`
- [ ] Add a weather-only command
- [ ] Add a system-health-only command
- [ ] Add a forex-only command
- [ ] Add a full daily-briefing command
- [ ] Add a trading-workspace command
- [ ] Add a Spotify command
- [ ] Add an unknown-command response
- [ ] Preserve the existing daily briefing workflow

Example commands:

- “Weather only”
- “Give me the system health”
- “What is the AED-to-peso rate?”
- “Start my daily briefing”
- “Open my trading workspace”
- “Play Spotify”

---

## Sprint 4.1 — Currency Amount Conversion 📋

Status: Planned

- [ ] Detect a spoken currency amount
- [ ] Convert AED to PHP
- [ ] Support questions such as “How much is 500 AED in pesos?”
- [ ] Validate unsupported or missing amounts
- [ ] Handle API failures safely

---

## Sprint 4.2 — Global Voice Interruption 📋

Status: Planned

Objective: Allow Marc to stop CLAP during any activity.

- [ ] Add a shared stop event
- [ ] Listen for “CLAP, stop”
- [ ] Stop active speech
- [ ] Stop background music
- [ ] Cancel remaining briefing actions
- [ ] Return CLAP safely to standby
- [ ] Prevent CLAP from reacting to its own voice

---

## Sprint 5.0 — Productivity Integrations 🔮

- [ ] Google Calendar integration
- [ ] Google Tasks integration
- [ ] Daily calendar summary
- [ ] Task reminders
- [ ] News briefing

---

## Sprint 6.0 — Smart Environment 🔮

- [ ] Smart-curtain control
- [ ] Smart-lighting control
- [ ] Morning-routine automation
- [ ] Presence detection
- [ ] Room environmental monitoring

---

## Containerization and Cloud Architecture 🔮

Objective: Use a hybrid design that preserves Windows hardware and desktop control.

- [ ] Separate desktop-control modules from service modules
- [ ] Keep microphone, speaker, and desktop automation on Windows
- [ ] Create a Python 3.13 Docker image
- [ ] Containerize weather and forex services
- [ ] Add an API between desktop CLAP and container services
- [ ] Evaluate Azure Container Apps
- [ ] Document local and cloud deployment options

---

## Milestones

### 2026-07-12 — Version 0.1: First Contact

- Double-clap detection
- Neural voice greeting
- Reusable voice engine
- GitHub project structure

### 2026-07-27 — Version 0.6 Release Candidate

- Spoken Yes/No responses
- Natural voice confirmation
- Keyboard fallback
- Background briefing music
- Python 3.13 virtual environment
- Reproducible dependency installation
- Updated README and roadmap