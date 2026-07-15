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









## Milestones

### 2026-07-12

Project CLAP officially completed Version 0.1 - First Contact.

Capabilities:

- Double clap detection
- Neural voice greeting
- Reusable voice engine
- GitHub project structure
