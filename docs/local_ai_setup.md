# CLAP Local AI Setup

## Purpose

CLAP uses Ollama as its local conversational AI engine.

Known automation commands continue to use CLAP's existing modules. Requests that are not recognized as commands are sent to the local AI for conversation, communication coaching, and interview practice.

## Requirements

- Windows 10 22H2 or newer
- Ollama for Windows
- Sufficient RAM for the selected model
- Python dependencies from `requirements.txt`

## Install Ollama

Download Ollama from:

https://ollama.com/download/windows

Verify the installation:

```powershell
ollama --version
```

## Download the Local Model

The current laptop uses the lightweight Llama 3.2 1B model:

```powershell
ollama run llama3.2:1b
```

Enter `/bye` to close the interactive Ollama session.

## CLAP Configuration

The selected model is configured in:

```text
src/conversation.py
```

Current setting:

```python
LOCAL_AI_MODEL = "llama3.2:1b"
```

## Run the Standalone Conversation Test

```powershell
.\.venv\Scripts\python.exe .\src\conversation.py
```

## Run CLAP

```powershell
.\.venv\Scripts\python.exe .\src\clap_detector.py
```

## Hybrid Routing

```text
Spoken request
    |
    +-- Known command --> Existing CLAP module
    |
    +-- Unknown request --> Local Ollama conversation
```

Examples of known commands:

- Weather
- System health
- Forex
- AED-to-PHP conversion
- TradingView charts
- Daily briefing
- Google Calendar schedule and availability
- Confirmed Google Calendar event creation

Examples of conversational requests:

- Interview practice
- Communication coaching
- Structured articulation training through `articulation_coach.py`
- Technical explanations
- General conversation

## Privacy and Limitations

- Ollama conversations are generated locally.
- Current information should come from approved live-data modules.
- The local model should not directly execute sensitive automation.
- Conversation history currently lasts only for the running session.
- Articulation progress is not persisted in the initial version.
- Google speech recognition and Edge TTS still require internet access.
