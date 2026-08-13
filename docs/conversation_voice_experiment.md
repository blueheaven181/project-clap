# Experimental Local Conversation Voice

## Purpose

This optional path advances the roadmap item to improve response speed and
streaming speech without changing trusted command routing or home-control
safety behavior. It streams text from the existing local Ollama model and
speaks sentence-sized chunks through CLAP's established voice engine.

The experiment is disabled by default. Missing or invalid configuration uses
the established non-streaming conversation path. A streaming failure before
speech begins also falls back to that path.

## Enable Locally

Copy:

```text
config/conversation_voice.example.json
```

to this ignored, user-controlled file:

```text
config/conversation_voice.local.json
```

Then set `enabled` to `true`. Do not place personal profile or memory data in
this file. The existing private profile remains the only personalization input.

## Scope and Safety

- Applies only inside `conversation.py`.
- Does not change `command_router.py`, Curtain confirmation, Bluetooth, clap
  activation, Spotify, desktop automation, or any other trusted command module.
- Uses the existing `greeting.speak` playback path, including its current
  physical double-clap speech-control behavior.
- Requires no new model or TTS download.
- Keeps `llama3.2:1b` as the configured rollback model.

## Current Limitation

This is streaming text with sentence-level speech, not full-duplex local
speech-to-speech. Edge TTS remains online. A later separately approved phase
can compare a local TTS engine after the user chooses a voice/model and accepts
the download size and dependency impact.
