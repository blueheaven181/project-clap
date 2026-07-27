# Project CLAP — Development Notes

This document records the technical issues, fixes, and lessons learned while developing Project CLAP.

---

# Issues and Fixes

## Issue Status

- 🔴 Open
- 🟡 Workaround in place
- 🟢 Resolved

---

## Python 3.14 Could Not Use PyAudio

**Status:** 🟢 Resolved

**Problem:**

Voice recognition failed with:

```text
AttributeError: Could not find PyAudio; check installation
```

**Cause:**

PyAudio was not readily available for the installed Python 3.14 environment.

**Solution:**

Python 3.13 was installed alongside Python 3.14. A project-specific virtual environment was created using Python 3.13:

```powershell
py -3.13 -m venv .venv
```

CLAP is now run using:

```powershell
.\.venv\Scripts\python.exe .\src\clap_detector.py
```

**Lesson:**

A computer can have multiple Python versions. A virtual environment controls which Python version and packages a project uses.

---

## PowerShell Blocked Virtual Environment Activation

**Status:** 🟡 Workaround in place

**Problem:**

PowerShell prevented `Activate.ps1` from running because script execution was disabled.

**Solution:**

The virtual environment's Python executable is called directly:

```powershell
.\.venv\Scripts\python.exe
```

**Lesson:**

Activating a virtual environment is convenient but not required. Calling its Python executable directly uses the same environment.

---

## Missing Python Packages

**Status:** 🟢 Resolved

**Problem:**

CLAP reported missing modules such as:

- `sounddevice`
- `edge_tts`
- `playsound`
- `requests`
- `psutil`
- `pygetwindow`
- `pyautogui`
- `pygame`

**Cause:**

The new Python 3.13 virtual environment started without CLAP's previously installed dependencies.

**Solution:**

The packages were installed inside `.venv`. A `requirements.txt` file was generated to record the environment.

Dependencies can be restored using:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Lesson:**

Packages are installed separately in each Python environment. Creating a new virtual environment does not copy packages from another Python installation.

---

## Voice Recognition Ended Too Quickly

**Status:** 🟢 Resolved

**Problem:**

CLAP displayed “Listening for response” but stopped before there was enough time to speak.

**Cause:**

Automatic speech detection did not reliably identify the beginning and end of speech using the laptop microphone.

**Solution:**

The built-in Realtek microphone was selected using `device_index=1`. CLAP was changed to record a fixed five-second window:

```python
audio = recognizer.record(source, duration=5)
```

**Lesson:**

Microphone sensitivity, background noise, and device selection affect automatic speech detection. Fixed-duration recording provides a predictable first implementation.

---

## Longer Yes/No Responses Were Not Recognized

**Status:** 🟢 Resolved

**Problem:**

A response such as “Yes, give me the daily briefing” did not equal the exact string `"yes"`.

**Solution:**

CLAP now checks whether an accepted confirmation word appears in the recognized sentence:

```python
yes_words = {"yes", "yeah", "yep", "sure", "okay", "ok"}


if any(word in response.split() for word in yes_words):
    ...
```

**Lesson:**

Natural speech should be interpreted by intent instead of requiring one exact sentence.

---

## Git Push Was Rejected

**Status:** 🟢 Resolved

**Problem:**

GitHub rejected a push because the remote `main` branch contained changes that were not available locally.

**Solution:**

Local uncommitted files were protected with a stash. Remote changes were then integrated using:

```powershell
git pull --rebase origin main
git push origin main
```

The local documentation files were restored and verified afterward.

**Lesson:**

A rejected push normally means the remote branch moved ahead. Local work should be protected before pulling or rebasing.

---

## Background Music File Is Not on GitHub

**Status:** 🟢 Expected behaviour

**Problem:**

`assets/briefing_music.mp3` does not appear in Git status or GitHub.

**Cause:**

The repository's `.gitignore` contains:

```text
*.mp3
```

**Decision:**

Keep the music file local to avoid committing a large or copyrighted audio file.

**Lesson:**

Gitignored files can still be required locally. Documentation should explain where the user needs to place them.

---

# Lessons Learned

## Python

### Indentation Controls Program Structure

Python uses indentation to determine which statements belong inside conditions, loops, functions, and exception handlers.

Incorrect indentation can change program behaviour even when the code looks almost correct.

### Imports Should Not Run Modules Automatically

Reusable modules should protect standalone test code with:

```python
if __name__ == "__main__":
    ...
```

This allows the module to be imported without automatically running its test code or main workflow.

### Virtual Environments Isolate Projects

A virtual environment gives CLAP its own Python version and packages.

CLAP currently uses Python 3.13 inside `.venv`, even though Python 3.14 is also installed on the computer.

### Exception Handling Protects the Workflow

External services and desktop automation can fail. `try`, `except`, and `finally` help CLAP recover safely.

A `finally` block is useful for cleanup, such as stopping background music even if a briefing module fails.

---

## Voice and Audio

### PyAudio Captures Microphone Audio

PyAudio provides microphone access to the SpeechRecognition library. It does not perform speech recognition by itself.

### Google Performs the Current Speech Recognition

CLAP currently uses:

```python
recognizer.recognize_google(...)
```

The recorded audio is sent to Google's speech-recognition service. Therefore, this feature requires an internet connection.

### Edge TTS Generates CLAP's Voice

`edge-tts` converts CLAP's text into spoken audio using Microsoft neural voices. It also requires an internet connection.

### Microphone Selection Matters

Windows may report many audio devices, including duplicate inputs and outputs.

The built-in Realtek microphone currently uses `device_index=1`. This number could change on another computer.

### Ambient Noise Affects Recognition

Fans, music, speakers, and room noise can affect the recognizer.

Background-noise calibration helps, but CLAP must not accidentally calibrate while its own voice or background music is playing.

### Fixed Recording Is Predictable but Limited

A five-second recording window solved the immediate microphone timing problem.

A future version should stop recording automatically after the user finishes speaking.

---

## Command Handling

### Natural Responses Are Not Exact Strings

A user may say:

- “Yes”
- “Yes, please”
- “Sure”
- “Okay, start the briefing”

Checking for recognized keywords makes CLAP feel more natural than comparing the entire response with `"yes"`.

### Commands Should Be Routed Centrally

Commands such as “weather only,” “open my workspace,” and “play Spotify” should eventually pass through one command router.

This will preserve the existing modules while giving CLAP one central place to understand user intent.

### Global Stop Requires Interruptible Operations

A true “CLAP, stop” feature must be capable of interrupting speech, background music, and remaining actions.

Blocking audio playback will eventually need to be replaced or controlled so another listener can stop it safely.

---

## Git and GitHub

### Git Status Is a Safety Check

Run:

```powershell
git status --short
```

before committing.

This displays modified and untracked files without changing anything.

### Stage Only the Intended Files

Using specific file paths helps prevent local settings, backups, generated audio, or unrelated files from being committed accidentally:

```powershell
git add docs/development_notes.md
```

### Pull Before Pushing When the Remote Is Ahead

If a push is rejected, protect local work first. Then integrate remote changes before trying to push again.

### Gitignore Protects Local and Generated Files

Virtual environments, generated speech files, cache folders, and local music should normally remain outside the GitHub repository.

---

## Software Engineering

### Preserve Working Features

CLAP should be improved incrementally. New functionality should connect to existing modules instead of replacing working code unnecessarily.

### Test Small Components First

Voice recognition and background music were tested independently before being connected to the complete clap-activated workflow.

This makes debugging easier because fewer components are involved in each test.

### Documentation Is Part of the Project

Each document has a different purpose:

- `README.md` explains the current project.
- `roadmap.md` describes planned development.
- The sprint retrospective reviews completed work.
- `development_notes.md` preserves problems, solutions, and reusable knowledge.
- `requirements.txt` records the Python dependencies.

### Software Development Is Iterative

Project CLAP improves through repeated cycles:

```text
Build → Test → Observe → Debug → Improve → Document
```

Problems encountered during development are not wasted time. They become reusable engineering knowledge.

---

# Current Technical Debt

The following features work or have temporary solutions but should be improved later:

- [ ] Move microphone `device_index=1` into a configuration file
- [ ] Replace the fixed five-second voice window with smarter listening
- [ ] Prevent CLAP from hearing and recognizing its own speech
- [ ] Add a reusable Yes/No response parser
- [ ] Add automated tests for voice-command parsing
- [ ] Gracefully handle a missing background-music file
- [ ] Review and simplify `requirements.txt`
- [ ] Add a central voice-command router
- [ ] Add a global “CLAP, stop” command
- [ ] Add “Hey CLAP” voice activation