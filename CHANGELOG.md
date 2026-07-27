# Changelog

All notable changes to Project CLAP are recorded in this document.

---

## Version 0.6 — Hands-Free Briefing

**Date:** 2026-07-28  
**Status:** Completed

### Added

- Voice-based Yes/No responses for the daily briefing
- Voice-based Yes/No responses for Spotify
- Support for natural responses such as:
  - “Yes, please”
  - “Yes, give me the daily briefing”
  - “No, I don't want to hear it”
  - “Sure”
  - “Okay”
- Five-second microphone recording window
- Built-in laptop microphone selection
- Keyboard fallback when voice recognition fails
- Background music during the spoken daily briefing
- Reusable `background_music.py` module
- Configurable background-music volume
- Smooth music fade-out after the briefing
- Python 3.13 virtual environment
- `requirements.txt` for dependency installation
- Updated project README
- Updated project roadmap
- Sprint retrospective documentation
- Development issues and lessons-learned documentation

### Changed

- Daily briefing confirmation changed from typed-only input to voice-first interaction
- Spotify confirmation changed from typed-only input to voice-first interaction
- Yes/No handling now checks keywords inside natural sentences
- CLAP now uses Python 3.13 for improved PyAudio compatibility
- The daily briefing workflow now starts and stops background music automatically
- Project documentation was updated to reflect the current architecture and functionality

### Fixed

- PyAudio compatibility problem with Python 3.14
- Voice recognition ending before the user had enough time to speak
- Incorrect microphone selection
- Longer spoken Yes responses not being accepted
- Missing dependencies in the new Python environment
- PowerShell virtual-environment activation limitation
- Git push rejection caused by the remote branch being ahead
- Background music continuing after briefing errors by using cleanup logic

### Tested

The complete workflow was tested successfully with both Yes and No responses:

```text
Double Clap
↓
CLAP is online
↓
Spoken briefing confirmation
↓
Background briefing music
↓
Weather briefing
↓
System health briefing
↓
Forex briefing
↓
Trading workspace automation
↓
Spoken Spotify confirmation
↓
Spotify playback or standby
```

### Known Limitations

- Voice recognition currently requires an internet connection
- Neural text-to-speech currently requires an internet connection
- Microphone device selection is fixed at `device_index=1`
- Voice recording uses a fixed five-second window
- CLAP cannot yet interrupt its own speech
- The background music file must be placed locally at:
  `assets/briefing_music.mp3`
- MP3 files are intentionally excluded from GitHub

---

## Version 0.5 — Interactive Daily Assistant

### Added

- Interactive daily briefing confirmation
- Weather briefing
- System health briefing
- Forex briefing
- AED-to-PHP conversion
- TradingView workspace automation
- Dual-monitor chart arrangement
- Spotify integration
- Spotify autoplay

### Interaction Method

Daily briefing and Spotify responses were entered using the keyboard.

---

## Version 0.4 — Workspace and Music Automation

### Added

- TradingView chart launching
- EUR/USD workspace
- GOLD workspace
- Multi-monitor window arrangement
- Spotify launching and playback automation

---

## Version 0.3 — Information Briefing

### Added

- Abu Dhabi weather information
- Temperature and feels-like temperature
- Humidity
- Wind speed
- Chance of rain
- Weather advisories
- CPU utilization
- Memory utilization
- Disk utilization
- System health recommendations
- EUR/USD rate
- GBP/USD rate
- USD/JPY rate
- AED-to-PHP conversion

---

## Version 0.2 — Intelligent Activation

### Added

- Double-clap detection
- Clap cooldown protection
- Reduced false clap detections
- Intelligent time-based greetings
- Morning, afternoon, and evening responses
- Reusable neural voice engine
- Temporary speech-file cleanup

---

## Version 0.1 — First Contact

### Added

- Initial Python project structure
- GitHub repository
- VS Code development environment
- First Python application
- First neural voice greeting
- Initial project documentation

---

## Planned for the Next Version

- Central voice-command router
- “Weather only” command
- “System health only” command
- Forex-only commands
- AED amount-to-peso conversion
- Trading workspace voice command
- Spotify voice command
- Global “CLAP, stop” command
- “Hey CLAP” voice activation
- “Good morning CLAP” morning-routine activation