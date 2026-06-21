

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Gemini_Live_API-Google-4285F4?style=for-the-badge&logo=google" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows" alt="Windows"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT"/>
</p>

<h1 align="center">🤖 JARVIS AI</h1>
<h3 align="center">Asistente de Voz con Inteligencia Artificial en Tiempo Real</h3>
<h4 align="center">Real-time AI Voice Assistant for Windows</h4>

---

https://github.com/user-attachments/assets/3c29e4e1-78de-4410-8fef-3814510f29f2

---

## ✨ Features

| Category | Capabilities |
|----------|-------------|
| **🎤 Real-time Voice** | Natural conversations with ultra-low latency via Gemini Live API. No need to wait for "wake words" — speak naturally. |
| **💬 WhatsApp** | Send messages to any contact, search and start chats, full keyboard automation (Ctrl+N → type → paste → send). |
| **🎵 Spotify** | Play/pause, next/previous track, volume control, **search and play any song** via Spotify Web API. |
| **📅 Google Calendar** | List events, create events, edit/delete directly by voice. |
| **📧 Gmail** | Read inbox, send emails, search messages, manage drafts. |
| **📁 Google Drive** | List files, search, upload, download, organize. |
| **🔔 Reminders** | One-time and recurring reminders (daily, weekly, specific days). Persistent across restarts via Windows Task Scheduler. |
| **🤖 Telegram Bot** | Remote control from your phone — send commands and receive responses anywhere. |
| **🖥️ PC Control** | Volume, brightness, open/close apps, window management, keyboard shortcuts, shutdown, restart, lock screen. |
| **⌨️ Type on Screen** | Tell JARVIS to type anything — it simulates keyboard input on any text field. |
| **🌤️ Weather** | Real-time weather reports, forecasts, and alerts. |
| **🌐 Web Search** | Internet search and information retrieval. |
| **🎬 YouTube** | Play videos, search, get trending content. |
| **📸 Screen Analysis** | Capture screen or webcam and ask questions about what you see. |
| **🎨 Cyberpunk UI** | Arc Reactor visualization with 160 particles, rotating holographic rings, reactive soundwave, and live HUD telemetry. |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         JARVIS AI                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │  Mic In  │───▶│  Gemini Live │───▶│  Audio Out (TTS)      │  │
│  │ (sound)  │    │  API (WebRTC)│    │  (sounddevice)        │  │
│  └──────────┘    └──────┬───────┘    └───────────────────────┘  │
│                         │                                        │
│                   ┌─────▼──────┐                                │
│                   │ Tool Dispatch│                               │
│                   │ (30+ tools) │                               │
│                   └─────┬──────┘                                │
│                         │                                        │
│    ┌────────────────────┼────────────────────┐                  │
│    ▼                    ▼                    ▼                  │
│  WhatsApp           Spotify             Google APIs             │
│  Telegram           Reminders           PC Control              │
│  Weather            Web Search          Screen Vision           │
│  YouTube            ...and more                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Concurrency Model

JARVIS uses **asyncio** with 5 parallel tasks under an `asyncio.TaskGroup`:
- `_listen_audio` — captures microphone input
- `_send_realtime` — streams audio to Gemini
- `_receive_audio` — receives AI responses and tool calls
- `_play_audio` — plays back audio responses
- `_watch_reconnect` — handles graceful reconnection on config changes

Each task is **error-isolated** — a transient failure in one task won't crash the entire session.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.12+** | Core language |
| **Google Gemini Live API** (`genai`) | Real-time voice AI with bidirectional audio streaming |
| **sounddevice** | Audio capture and playback |
| **numpy** | Audio signal processing and gain amplification |
| **Tkinter** | Custom Cyberpunk Arc Reactor UI |
| **pywinauto** | Windows GUI automation (WhatsApp, keyboard) |
| **pyautogui** | Keyboard simulation and screen capture |
| **spotipy** | Spotify Web API integration |
| **Google APIs** (Calendar, Gmail, Drive) | Cloud productivity suite |
| **python-telegram-bot** | Remote control via Telegram |
| **pycaw** | Windows audio session volume control |
| **Pillow + opencv-python** | Screen/image capture and processing |
| **requests, httpx, aiohttp** | HTTP client stack |

---

## 📋 Prerequisites

- **Windows 10/11**
- **Python 3.12+**
- **Git**
- **Google Gemini API key** ([Get one here](https://aistudio.google.com/))
- **Spotify Premium** (for search & playback)
- **Telegram Bot Token** (optional, for remote control)

---

## 🔧 Installation

```bash
# 1. Clone the repository
git clone https://github.com/Jonas26-hash/JARVIS-AI-Asistente-de-Voz-con-Inteligencia-Artificial-en-Tiempo-Real.git
cd JARVIS-AI-Asistente-de-Voz-con-Inteligencia-Artificial-en-Tiempo-Real

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys (see next section)
```

---

## ⚙️ Configuration

Copy `config/api_keys.example.json` to `config/api_keys.json` and fill in your keys:

```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY",
  "spotify_client_id": "YOUR_SPOTIFY_CLIENT_ID",
  "spotify_client_secret": "YOUR_SPOTIFY_CLIENT_SECRET",
  "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "tmdb_api_key": "YOUR_TMDB_API_KEY",
  "timezone": "America/Lima",
  "language": "es",
  "location_city": "Lima",
  "mic_device": 1,
  "spk_device": 1
}
```

> **Note:** `api_keys.json` is in `.gitignore` and will NOT be committed. Your keys stay local.

---

## 🚀 Usage

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run JARVIS
python main.py
```

Speak naturally to JARVIS:

| You say | JARVIS does |
|---------|-------------|
| *"Abrí WhatsApp y mandale un mensaje a mamá que llego en 10 minutos"* | Opens WhatsApp, searches contact, types and sends message |
| *"Pon música de Queen"* | Searches Spotify and starts playing Queen |
| *"Recuérdame a las 7 PM llamar al médico"* | Creates persistent reminder with Task Scheduler |
| *"¿Qué recordatorios tengo?"* | Lists all pending reminders with time remaining |
| *"Escribe en el bloc de notas: lista de compras"* | Types text on screen via keyboard simulation |
| *"Baja el volumen al 30%"* | Adjusts system volume |
| *"¿Qué clima hace mañana?"* | Fetches weather forecast |

---

## 🧰 Available Tools

| Tool | Description |
|------|-------------|
| `whatsapp` | Send messages, open chats, manage WhatsApp Desktop |
| `spotify_control` | Play, pause, skip, search, play playlists, volume |
| `reminder` | Set/list/delete one-time or recurring reminders |
| `type_writer` | Type text on screen via simulated keyboard |
| `send_message` | Multi-platform messaging (WhatsApp, Telegram, SMS) |
| `weather_report` | Current weather and forecasts |
| `web_search` | Internet search and information retrieval |
| `youtube_video` | Play, search, trending YouTube videos |
| `google_calendar` | List, create, edit, delete calendar events |
| `gmail_control` | Read, send, search emails |
| `google_drive` | List, search, upload files |
| `computer_settings` | Volume, brightness, dark mode, WiFi, shutdown |
| `computer_control` | Click, type, hotkeys, mouse, scroll, screenshots |
| `desktop_control` | Wallpaper, organize desktop, system stats |
| `browser_control` | Navigate, search, fill forms, manage tabs |
| `screen_process` | Capture and analyze screen/webcam with AI vision |
| `telegram_bot` | Remote control via Telegram |
| `rgb_control` | RGB lighting control |
| `game_updater` | Game updates management |
| `file_processor` | File operations and processing |
| `flight_finder` | Flight search and tracking |
| `accessibility` | Accessibility features and screen reading |
| `news` | Latest news headlines |

---

## 📁 Project Structure

```
JARVIS/
├── main.py                    # Entry point — session lifecycle, tool dispatch
├── ui.py                      # Cyberpunk Arc Reactor UI (Tkinter)
├── beta_config.py             # API key management & rotation
├── core/
│   ├── prompt.txt             # System prompt for Gemini
│   ├── sounds.py              # Audio feedback sounds
│   └── ... 
├── actions/
│   ├── whatsapp.py            # WhatsApp automation
│   ├── spotify_control.py     # Spotify media keys + API
│   ├── reminder.py            # Persistent reminders
│   ├── type_writer.py         # Keyboard typing tool
│   ├── google_calendar.py     # Google Calendar integration
│   ├── gmail_control.py       # Gmail integration
│   ├── weather_report.py      # Weather forecasts
│   ├── browser_control.pyc    # Browser automation
│   ├── computer_control.pyc   # PC direct control
│   └── ... (30+ action modules)
├── memory/
│   ├── memory_manager.pyc     # Long-term memory management
│   └── long_term.json         # Persistent memory storage
├── config/
│   ├── api_keys.example.json  # API key template (safe to commit)
│   └── api_keys.json          # ⚠️ Your actual keys (gitignored)
├── .gitignore
└── README.md
```

> **Note:** Some modules are distributed as `.pyc` (compiled bytecode) for optimization. The source equivalents will be published as they are refactored.

---

## 🎨 UI Preview

The Cyberpunk Arc Reactor interface features:
- **Swirling vortex particles** (160 particles with enhanced trails)
- **Rotating holographic rings**
- **Reactive soundwave** that pulses with your voice
- **Glowing HUD telemetry** (connection status, audio levels, system time)
- **Central energy core** with pulsing glow

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** for the groundbreaking Live API
- The **Python community** for the incredible ecosystem of libraries
- **You** — for checking out this project!

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/Jonas26-hash">Jonas26-hash</a>
</p>
