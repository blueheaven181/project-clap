# Project CLAP Requirements

## Functional Requirements

### Activation and Voice

- CLAP shall activate through a physical double clap or the local “Hey CLAP”
  wake word.
- CLAP shall provide a time-based spoken greeting after activation.
- CLAP shall accept natural spoken commands and follow-up commands.
- CLAP shall delay speech-control arming after activation to prevent the
  activation sound from pausing its own greeting.
- CLAP shall allow active speech to be paused only by a validated physical
  double clap.
- CLAP shall reject spoken commands and ordinary voice activity as pause
  triggers.
- After a double-clap pause, CLAP shall accept continue, repeat, and stop.

### Information and Automation

- CLAP shall retrieve and speak Abu Dhabi weather.
- CLAP shall report CPU, memory, and disk utilization.
- CLAP shall retrieve forex rates and convert spoken AED amounts to PHP.
- CLAP shall retrieve categorized live news.
- CLAP shall open and arrange the configured trading workspace.
- CLAP shall control Spotify and Windows system volume through approved
  commands.

### Daily Briefing

- CLAP shall provide a daily briefing containing weather, system health,
  forex, and today's Google Calendar schedule.
- CLAP shall coordinate briefing speech with background music.
- Stopping the briefing shall prevent subsequent workspace and Spotify actions.

### Google Calendar

- CLAP shall read today's schedule and remaining availability.
- CLAP shall understand simple event requests for today and tomorrow.
- CLAP shall accept both `PM` and speech-recognition forms such as `p.m.`.
- CLAP shall require explicit confirmation before creating an event.
- CLAP shall create timed events using `Asia/Dubai`.
- CLAP shall inherit the Calendar account's default event reminders.
- OAuth credentials and tokens shall remain outside Git.

### Google Tasks

- CLAP shall read incomplete tasks from the user's default task list.
- CLAP shall report all pending tasks or only pending tasks due today or
  tomorrow.
- CLAP shall preserve task titles and optional due dates in API payloads.
- Spoken task dates shall be interpreted using `Asia/Dubai`.
- CLAP shall require explicit spoken confirmation before creating a task.
- A failed or unrecognized confirmation shall not create a task.
- CLAP shall not delete, complete, rename, or otherwise modify existing tasks.
- CLAP shall request only the Google Tasks scope needed for reading and
  creating tasks, and shall safely reauthorize Calendar-only local tokens.

### Local AI

- CLAP shall route unknown conversational requests to a local Ollama model.
- The local AI shall not execute arbitrary operating-system commands.
- Approved automation shall remain inside dedicated trusted modules.

### Articulation Training

- CLAP shall provide a dedicated articulation-training voice command.
- Each session shall present one speaking exercise and listen for an answer.
- Feedback shall identify one strength and one priority improvement.
- A clearer example shall not invent personal or professional facts.
- CLAP shall offer an optional retry after feedback.

## Non-Functional Requirements

- CLAP shall run on Windows 11 with Python 3.13.
- CLAP shall recover gracefully from network and API failures.
- Secrets and private local configuration shall not be committed.
- New functionality shall preserve existing trusted commands.
- Sensitive or externally mutating actions shall require confirmation.
- Changed Python files shall compile before a checkpoint.
- Automated tests shall cover testable parsing and routing behavior.

## Planned Requirements

- Improve wake-word reliability at longer distances.
- Replace fixed-duration voice recording with smarter listening.
- Add SwitchBot Curtain 3 and smart-lighting controls.
- Package CLAP as a Windows application.
- Evaluate a secure mobile companion.
