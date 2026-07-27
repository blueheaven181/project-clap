# 👏 CLAP

## Clap-Activated Personal Assistant

CLAP is a Python-based desktop assistant activated by a double clap. It provides voice-controlled daily briefings, system information, trading workspace automation, and music playback to help start the day efficiently.

---

## 🚀 Current Features

### Activation

- Double-clap detection
- Clap cooldown and double-clap timing controls

### Greetings

- Intelligent time-based greetings
- Microsoft neural text-to-speech voice

### Voice Recognition

- Spoken Yes/No responses
- Natural responses such as “Yes, start my daily briefing”
- Voice-controlled Spotify confirmation
- Keyboard fallback when voice recognition fails
- Microphone and recognition error handling

### Interactive Daily Briefing

- Asks whether the user wants the daily briefing
- Accepts spoken confirmation before execution
- Plays quiet background music during the briefing
- Stops background music safely when the briefing finishes

### Weather

- Current Abu Dhabi weather
- Temperature
- Feels-like temperature
- Humidity
- Wind speed
- Chance of rain
- Weather advisories

### System Health

- CPU utilization
- Memory utilization
- Disk utilization
- Health recommendations

### Forex

- EUR/USD
- GBP/USD
- USD/JPY
- AED-to-PHP conversion

### Trading Workspace Automation

- Opens the EUR/USD TradingView chart
- Opens the GOLD TradingView chart
- Automatically arranges charts across dual monitors

### Spotify

- Optional Spotify launch
- Spoken Yes/No confirmation
- Automatic playback

---

## 🔄 Current Workflow

```text
Double Clap
    ↓
CLAP is online
    ↓
Would you like to hear your daily briefing?
    ↓
Spoken Yes/No Response
    ↓
YES
    ↓
Background Music Starts
    ↓
Weather Briefing
    ↓
System Health Briefing
    ↓
Forex Briefing
    ↓
Background Music Stops
    ↓
Trading Workspace Automation
    ↓
Daily Briefing Complete
    ↓
Would you like me to launch Spotify?
    ↓
Spoken Yes/No Response
    ↓
Optional Spotify Autoplay


---

## 📂 Project Structure

```text
project-clap
│
├── assets
│   └── briefing_music.mp3   # Local file; excluded from Git
│
├── config
├── docs
├── tests
│
├── src
│   ├── background_music.py
│   ├── clap_detector.py
│   ├── forex.py
│   ├── greeting.py
│   ├── main.py
│   ├── neural_voice.py
│   ├── spotify.py
│   ├── system_health.py
│   ├── voice_commands.py
│   ├── weather.py
│   └── workspace.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Development Environment

CLAP currently uses Python 3.13 because PyAudio support is required for microphone input.

Create a project environment:

```powershell
py -3.13 -m venv .venv
```

Install the dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run CLAP:

```powershell
.\.venv\Scripts\python.exe .\src\clap_detector.py
```

The following features require an internet connection:

- Neural text-to-speech through `edge-tts`
- Google speech recognition
- Weather information
- Forex information

---

## 🏆 Current Status

### Version 0.6 Release Candidate — Hands-Free Briefing

Completed:

- ✅ Double-clap activation
- ✅ Neural voice greeting
- ✅ Spoken briefing confirmation
- ✅ Voice-recognition fallback handling
- ✅ Weather briefing
- ✅ System-health briefing
- ✅ Forex briefing
- ✅ AED-to-PHP conversion
- ✅ Background briefing music
- ✅ TradingView automation
- ✅ Dual-monitor workspace automation
- ✅ Spoken Spotify confirmation
- ✅ Spotify autoplay
- ✅ Python 3.13 virtual environment
- ✅ Reproducible dependency installation

---

## 🔮 Roadmap

### Version 0.7 — Voice Command Routing

- [ ] Ask “How can I help?” after activation
- [ ] Weather-only command
- [ ] System-health-only command
- [ ] Forex-only command
- [ ] AED-to-PHP amount conversion
- [ ] Full daily-briefing command
- [ ] Trading-workspace command
- [ ] Spotify command
- [ ] Unknown-command response

### Global Interruption

- [ ] Global “CLAP, stop” voice command
- [ ] Stop active speech
- [ ] Stop background music
- [ ] Cancel remaining briefing actions
- [ ] Return safely to standby mode

### Productivity Integrations

- [ ] Google Calendar integration
- [ ] Google Tasks integration
- [ ] Daily schedule summary
- [ ] Task reminders
- [ ] News briefing

### Smart Environment

- [ ] Smart-curtain control
- [ ] Smart-lighting control
- [ ] Morning-routine automation
- [ ] Presence detection
- [ ] Room environmental monitoring

### Architecture and Deployment

- [ ] Separate desktop-control and service modules
- [ ] Introduce a command router
- [ ] Evaluate offline voice recognition
- [ ] Containerize weather and forex services
- [ ] Connect desktop CLAP to containerized services
- [ ] Evaluate Azure Container Apps

---

## 🧠 Development Philosophy

CLAP is both a personal assistant and a practical learning project.

The project is used to learn:

- Python programming
- Software architecture
- Automation
- API integration
- Voice interaction
- Git and GitHub
- Documentation
- Debugging and troubleshooting

Development favors small, testable improvements while preserving working functionality.

---

## 👨‍💻 Author

Marc Anthony Marquez

NOC Engineer | Azure Administrator | Automation Enthusiast