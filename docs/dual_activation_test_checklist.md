CLAP Dual-Activation Stability Checklist

## Test Legend

- ✅ Passed
- ❌ Failed
- ⬜ Not tested



Preparation
[✅] Start CLAP:
    .\.venv\Scripts\python.exe .\src\clap_detector.py

[✅] Terminal shows:
    Listening for double clap or Hey CLAP...


Double-Clap Tests
[✅] Double hand clap activates CLAP
[✅] Terminal shows: DOUBLE CLAP DETECTED
[✅ ] CLAP gives only one greeting
[✅] One clap alone does not activate CLAP
[✅] Normal speech does not activate the clap detector
[✅] Table/keyboard sounds do not cause unwanted activation


Wake-Word Tests
[✅] Say “Hey CLAP”
[✅] Terminal shows: HEY CLAP DETECTED
[✅] It does not incorrectly show: DOUBLE CLAP DETECTED
[✅] CLAP gives only one greeting
[✅] Normal conversation without “Hey CLAP” does not activate it
[✅] Test “Hey CLAP” three to five times


Command Tests
[ ] Activate with double clap, then say “weather”
[ ] Weather report is spoken correctly
[ ] CLAP asks: “Is there anything else I can help you with?”
[ ] Say “system health”
[ ] System-health report is spoken correctly
[ ] Say “no”
[ ] CLAP says: “Okay Marc, standing by”
[ ] CLAP returns to listening mode without immediately reactivating


Second Activation Method
[ ] Activate with “Hey CLAP”
[ ] Request an AED-to-PHP conversion
[ ] Conversion is spoken correctly
[ ] Request another command when prompted
[ ] Say “no” to end the interaction
[ ] CLAP returns to listening mode without immediately reactivating


Daily Briefing
[ ] Activate CLAP
[ ] Say “daily briefing”
[ ] Weather, system health, and forex are spoken
[ ] Background music starts and stops correctly
[ ] Trading charts open and arrange correctly
[ ] Spotify question is asked
[ ] Both “yes” and “no” Spotify responses work


Longer Stability Test
[ ] Leave CLAP listening for 5–10 minutes
[ ] No false double-clap activations
[ ] No false wake-word activations
[ ] No repeated microphone-overflow messages
[ ] Ctrl+C stops CLAP cleanly


Result
Double clap: PASS / FAIL
Hey CLAP: PASS / FAIL
Direct commands: PASS / FAIL
Follow-up commands: PASS / FAIL
Daily briefing: PASS / FAIL
False activations: NONE / OBSERVED
Errors encountered: