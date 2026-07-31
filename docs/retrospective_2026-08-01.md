# Google Calendar Integration Retrospective

**Date:** 2026-08-01
**Status:** Completed checkpoint

## Objective

Add useful Google Calendar voice workflows without breaking CLAP's existing
commands, daily briefing, speech confirmation, or local-first security model.

## Delivered

- Today's schedule, remaining events, and free-time reporting
- Calendar schedule in the daily briefing
- Simple event parsing for today and tomorrow
- Spoken confirmation before event creation
- `Asia/Dubai` timezone-aware event payloads
- Verified Gulf Standard Time in the Google Calendar web interface
- Google Calendar default reminders
- Support for speech transcripts containing dotted `a.m.` and `p.m.`
- Daily-briefing intent aliases, including the common “daily breathing” variant
- A three-second guard before speech-control claps are armed after activation
- Automated parsing, payload, confirmation, routing, and briefing-intent tests

## Problems Found

### 7:00 PM appeared as 3:00 PM

The API stored `19:00+04:00` as the equivalent UTC instant `15:00Z`. The code
was correct; the Google Calendar interface needed Gulf Standard Time as its
display timezone.

### Event creation fell through to schedule reading

Google speech recognition returned `p.m.` while the parser originally accepted
only `pm`. Normalizing dotted meridiem notation fixed the routing.

### Daily briefing entered pause control

Trailing wake-word audio generated clap-like peaks while CLAP began speaking.
A short arming delay now separates activation from speech control.

### Calendar routing blocked later commands

An unconditional return after the schedule branch made later command handlers
unreachable. Moving the return inside the Calendar branch restored weather,
news, volume, Spotify, and other routes.

## Verification

- Affected Python files compile successfully.
- Eleven automated regression tests pass.
- Live schedule, availability, and free-time reads succeed.
- Calendar credentials and tokens remain ignored and untracked.
- Local `main` and `origin/main` were synchronized at each checkpoint.

## Lessons

- Separate timezone storage from timezone display during diagnosis.
- Test with real speech-recognition transcripts, including punctuation.
- Shared audio signals need explicit state-transition guards.
- A trusted-command router needs regression tests that protect unrelated
  commands from early returns.

## Next Increment

Continue Sprint 5.2 with Google Tasks reading first, then add task creation with
explicit spoken confirmation.
