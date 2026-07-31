# CLAP Dual-Activation Stability Checklist

## Test Legend

- ✅ Passed
- ❌ Failed
- ⬜ Not tested



## Preparation
[✅] Start CLAP:
    .\.venv\Scripts\python.exe .\src\clap_detector.py

[✅] Terminal shows:
    Listening for double clap or Hey CLAP...


## Double-Clap Tests
[✅] Double hand clap activates CLAP
[✅] Terminal shows: DOUBLE CLAP DETECTED
[✅ ] CLAP gives only one greeting
[✅] One clap alone does not activate CLAP
[✅] Normal speech does not activate the clap detector
[✅] Table/keyboard sounds do not cause unwanted activation


## Wake-Word Tests
[✅] Say “Hey CLAP”
[✅] Terminal shows: HEY CLAP DETECTED
[✅] It does not incorrectly show: DOUBLE CLAP DETECTED
[✅] CLAP gives only one greeting
[✅] Normal conversation without “Hey CLAP” does not activate it
[✅] Test “Hey CLAP” three to five times
[ ] Confirm “Hey CLAP” does not immediately trigger speech-control pause
[ ] Confirm the greeting reaches “How can I help?” normally


## Command Tests
[✅] Activate with double clap, then say “weather”
[✅] Weather report is spoken correctly
[✅] CLAP asks: “Is there anything else I can help you with?”
[✅] Say “system health”
[✅] System-health report is spoken correctly
[✅] Say “no”
[✅] CLAP says: “Okay Marc, standing by”
[✅] CLAP returns to listening mode without immediately reactivating


## Second Activation Method
[✅] Activate with “Hey CLAP”
[✅] Request an AED-to-PHP conversion
[✅] Conversion is spoken correctly
[✅] Request another command when prompted
[✅] Say “no” to end the interaction
[✅] CLAP returns to listening mode without immediately reactivating


## Daily Briefing
[✅] Activate CLAP
[✅] Say “daily briefing”
[✅] Weather, system health, and forex are spoken
[ ] Today's Google Calendar schedule is spoken
[✅] Background music starts and stops correctly
[✅] Trading charts open and arrange correctly
[✅] Spotify question is asked
[✅] Both “yes” and “no” Spotify responses work


## Longer Stability Test
[✅] Leave CLAP listening for 5–10 minutes
[✅] No false double-clap activations
[✅] No false wake-word activations
[✅] No repeated microphone-overflow messages
[✅] Ctrl+C stops CLAP cleanly


## Result
Double clap: PASS
Hey CLAP: PASS
Direct commands: PASS
Follow-up commands: PASS
Daily briefing: PASS
False activations: NONE
Errors encountered:


## Calendar Command Tests
[ ] Say “What is on my schedule today?”
[ ] Say “When am I free today?”
[ ] Say “Schedule a test event tomorrow at 7:00 p.m.”
[ ] Confirm CLAP asks before creating the event
[ ] Say “no” and verify no event is created
[ ] Repeat, say “yes,” and verify the event appears at 7:00 PM
