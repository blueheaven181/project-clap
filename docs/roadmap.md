# Roadmap


## Sprint 0 - Foundation ✅

Completed

- GitHub Repository
- Documentation
- Architecture
- Requirements
- Initial Setup

---

## Sprint 1 - First Contact ✅

Completed

- Python Installation
- VS Code Setup
- GitHub Desktop Setup
- First Python Application
- First Voice Greeting

---



## Sprint 1.2 - Voice Engine ✅

Status: Completed

Objective:

Create a reusable voice engine that can be used across all Project CLAP modules.

Tasks:

- [X] Create greeting.py
- [X] Move GuyNeural voice code into reusable function
- [X] Create speak() method
- [X] Test voice output
- [X] Integrate with main.py

Success Criteria:

Project CLAP can say:

"Good morning Marc"

using:

from greeting import speak

speak("Good morning Marc")


## Sprint 1.3 - Double Clap Detection ✅

Status: Completed

Objective:

Allow Project CLAP to activate through a double clap.

Tasks:

- [x] Install sounddevice
- [x] Detect audio input
- [x] Detect double clap
- [x] Trigger voice greeting
- [x] Test clap activation

Success Criteria:

👏 Clap
👏 Clap

↓

Project CLAP Activated

↓

"Good evening Marc. Project CLAP activated."



## Sprint 2.0 - Intelligent Greeting ✅

Status: Completed

Objective:

Make Project CLAP aware of the current time and
deliver the appropriate greeting.

Tasks:

- [x] Detect current time
- [x] Determine greeting
- [x] Integrate with greeting.py
- [x] Update main.py
- [x] Update clap activation greeting

Success Criteria:

Morning:
Good morning Marc

Afternoon:
Good afternoon Marc

Evening:
Good evening Marc


## Sprint 2.0.1 - Stability Improvements ✅

Status: Completed

Objective:

Improve reliability of Project CLAP activation and voice playback.

Tasks:

- [x] Fix startup greeting issue
- [x] Fix incorrect time-based greeting
- [x] Calibrate clap detection threshold
- [x] Add clap cooldown protection
- [x] Reduce false clap detections
- [x] Clean up temporary audio files
- [x] Update .gitignore for generated MP3 files

Success Criteria:

Run Project CLAP

↓

Listening for claps...

↓

👏 👏

↓

DOUBLE CLAP DETECTED

↓

Good morning / afternoon / evening Marc

↓

No false activations


## Sprint 2.1 - Weather Module 🚧

Status: In Progress

Objective:

Provide live weather information for Abu Dhabi.

Tasks:

- [x] Install requests
- [x] Create weather.py
- [x] Retrieve weather data
- [x] Display weather information
- [ ] Integrate with voice engine
- [ ] Integrate with Project CLAP activation

Success Criteria:

Weather in Abu Dhabi is 35 degrees Celsius with Clear.


## Milestones

### 2026-07-12

Project CLAP officially completed Version 0.1 - First Contact.

Capabilities:

- Double clap detection
- Neural voice greeting
- Reusable voice engine
- GitHub project structure
