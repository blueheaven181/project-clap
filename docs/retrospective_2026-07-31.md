# Project CLAP Sprint Retrospective

Date: 2026-07-31
Release: Version 0.7 Development Milestone
Focus: Dual Activation, Command Routing, Local AI, Media Control, Interruption, and Live News

## Sprint Goals

The main goals were:

- Add “Hey CLAP” alongside double-clap activation
- Introduce direct voice commands
- Support follow-up requests without repeated greetings
- Add a local conversational AI engine
- Improve Spotify and Windows audio control
- Allow briefing speech to be paused, repeated, continued, or stopped
- Add current categorized news
- Preserve all existing CLAP functionality
- Maintain security and privacy boundaries

## What Was Completed

### Dual Activation

- Installed OpenWakeWord
- Tested the supplied “Hey Jarvis” model
- Trained a custom “Hey CLAP” model in Google Colab
- Added the ONNX wake-word model to CLAP
- Integrated wake-word and double-clap detection
- Added activation cooldown protection
- Reduced false clap activations from normal speech
- Prevented “Hey CLAP” from being interpreted as a double clap
- Kept double clap as the reliable primary activation method

### Command Routing

- Created `command_router.py`
- Added trusted routes for:
  - Weather
  - System health
  - Forex
  - AED-to-PHP conversion
  - TradingView
  - Spotify
  - Windows system volume
  - Live news
- Added follow-up commands
- Added safe “no,” “stop,” and standby handling
- Routed general questions to conversation mode
- Preserved existing dedicated modules

### Local AI Conversation

- Installed Ollama
- Tested different local model sizes
- Selected `llama3.2:1b` for better laptop performance
- Created `conversation.py`
- Added conversation history
- Added communication and articulation coaching
- Added interview and career coaching
- Added fitness coaching
- Added exit phrases
- Added inactivity handling
- Added conversation continuation confirmation
- Created a private local profile
- Kept private profile data outside GitHub
- Prevented the AI from claiming live information without an approved module

### Spotify and System Audio

- Added Spotify pause, resume, stop, next, and previous controls
- Added private mood-playlist configuration
- Added relaxing-music playback
- Created `system_volume.py`
- Added exact volume setting
- Added relative volume increase and decrease
- Added mute and unmute controls

### Speech and Briefing Interruption

- Replaced `playsound` playback with a dedicated `pygame` speech channel
- Added pause, continue, repeat, and stop support
- Used double clap as the reliable interruption signal
- Paused background music with speech
- Resumed background music after continue or repeat
- Stopped background music after a full stop
- Cancelled remaining briefing actions after stop
- Prevented stopped briefings from continuing into system health, forex, charts, or Spotify
- Returned CLAP safely to standby

### Live News

- Created `news.py`
- Added current general news
- Added artificial intelligence news
- Added technology news
- Added cybersecurity news
- Added forex news
- Included publication sources
- Limited spoken headline counts
- Added network and RSS parsing error handling
- Completed end-to-end voice testing

### Documentation and Security

- Added a dual-activation checklist
- Added local AI setup documentation
- Expanded private configuration exclusions
- Reviewed ignored credentials and generated files
- Updated the README
- Updated the roadmap
- Updated the changelog
- Preserved the Version 0.6 retrospective as historical documentation

## What Went Well

- CLAP evolved without rewriting working modules
- Double clap remained dependable while wake-word testing continued
- Dedicated modules kept trusted automation separate from local AI
- Features were tested independently before integration
- Small commits provided recovery points
- Syntax checks caught indentation problems before runtime
- Voice follow-up commands made CLAP feel less repetitive
- Local AI worked without a paid API
- Private information remained outside GitHub
- Speech and background music were successfully coordinated
- The full briefing could be stopped cleanly
- Live news worked across all requested categories
- Marc gained practical experience with Python imports, functions, loops, conditions, exceptions, audio processing, APIs, local AI, and Git

## Challenges Encountered

### Custom Wake-Word Training

Training “Hey CLAP” required Google Colab, multiple compatibility fixes, model dependencies, generated audio samples, feature generation, and ONNX export.

The first model achieved useful close-range recognition but limited recall. Recognition becomes less reliable farther from the laptop.

### Clap and Speech Separation

Normal speech initially triggered the clap detector. Volume alone was not enough to distinguish speech from a clap.

Sharpness filtering and wake-word score checks reduced false activation while preserving physical claps.

### Python Indentation

As `clap_detector.py` grew, nested `if`, `else`, `while`, `try`, and `finally` blocks became harder to maintain. Several runtime problems were caused by code belonging to the wrong block.

### Voice Recognition

The recognizer sometimes misunderstood commands, added unrelated words, or failed when the room was noisy. Music and CLAP’s own speech also made direct voice interruption unreliable.

### Speech Interruption

Listening for “CLAP, stop” while CLAP was speaking was inconsistent because the microphone also heard the laptop speaker.

A reliable design was implemented:

1. Double clap pauses speech.
2. Background music pauses.
3. Marc says continue, repeat, or stop.
4. CLAP performs the selected action.

### Local AI Performance

Larger local models responded slowly on the current laptop. The smaller `llama3.2:1b` model responded faster but sometimes produced weaker answers.

### Temporary Speech Files

Interrupted sessions left generated MP3 files behind. Cleanup was improved with `try`, `finally`, unique filenames, and startup cleanup.

### Git and Documentation

Experimental files, private configuration, generated audio, and production files needed to remain clearly separated. Selective `git add` commands prevented unrelated work from entering commits.

## Lessons Learned

- Audio volume alone cannot reliably identify a clap
- Wake-word thresholds balance sensitivity against false activation
- A lower threshold detects quieter speech but increases false positives
- Model quality is more important than continually lowering the threshold
- Double clap is a useful hardware-independent interruption signal
- Speech playback needs a controllable audio channel for pause and resume
- Background music and speech must share control state
- A stop action must cancel the workflow, not only the current audio
- Trusted commands should remain separate from generative AI
- Local AI can work without API charges after models are downloaded
- Smaller AI models are faster but less capable
- Personalization should use private local configuration
- External live information should come from approved online modules
- Long Python files become difficult to maintain
- Compilation checks validate syntax but do not prove correct behavior
- End-to-end testing remains necessary
- Incremental commits make experimentation safer

## Technical Debt

The following items should be improved:

- Split `clap_detector.py` into smaller modules
- Create a reusable activation manager
- Create a reusable interaction-session manager
- Move thresholds and microphone selection into configuration
- Replace fixed-duration voice recording with smarter listening
- Improve wake-word training and long-distance recognition
- Improve echo handling during speech
- Add automated command-router tests
- Add automated workflow-state tests
- Add structured logging
- Add better news filtering and duplicate removal
- Add source allowlists for news
- Review and simplify imports
- Decide whether experimental speech-control files should be retained
- Review old README backup files and remaining local Git artifacts
- Prepare a clean Windows application entry point

## Security Review

The sprint maintained the following boundaries:

- Private profile data is excluded from GitHub
- Spotify playlist details remain local
- Credentials and secrets are ignored
- Temporary speech files are excluded and cleaned
- Local AI does not execute arbitrary system commands
- Trusted automation remains in dedicated modules
- Live services include error handling
- Future sensitive actions should require confirmation
- External integrations should use minimum required permissions

## Next Sprint

The next hardware-focused sprint is SwitchBot Curtain 3 integration.

Planned steps:

- Install and calibrate the curtain device
- Confirm mobile application control
- Confirm local Bluetooth capability
- Test Bluetooth communication separately
- Create a dedicated curtain module
- Add open, close, and percentage commands
- Add connection and timeout handling
- Integrate the module with the trusted command router
- Preserve manual and mobile control
- Document the security boundary

Parallel software improvements may include:

- Adding news to the daily briefing
- Improving wake-word reliability
- Refactoring `clap_detector.py`
- Expanding communication and interview coaching
- Preparing Google Calendar and Google Tasks integration

## Sprint Result

The sprint was successful.

CLAP progressed from a hands-free daily briefing assistant into a hybrid intelligent assistant with dual activation, trusted voice commands, local AI conversation, private personalization, controllable speech, media control, system-volume control, and live news.

The project now has the beginnings of both a brain and a control system: local AI handles conversation, while dedicated modules safely handle real actions.