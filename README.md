
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Gemini_Live_API-Google-4285F4?style=for-the-badge&logo=google" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows" alt="Windows"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT"/>
</p>

<h1 align="center">🤖 JARVIS AI</h1>
<h3 align="center">Asistente de Voz con Inteligencia Artificial en Tiempo Real</h3>

---

## ✨ Funcionalidades

| Categoría | Capacidades |
|-----------|-------------|
| **🎤 Voz en Tiempo Real** | Conversaciones naturales con latencia ultra baja vía Gemini Live API. Sin palabras de activación — habla con naturalidad. |
| **💬 WhatsApp** | Envía mensajes a cualquier contacto, busca e inicia chats, automatización completa por teclado (Ctrl+N → escribe → pega → envía). |
| **🎵 Spotify** | Reproducir/pausar, siguiente/anterior, control de volumen, **buscar y reproducir cualquier canción** vía Spotify Web API. |
| **📅 Google Calendar** | Listar eventos, crear, editar, eliminar directamente por voz. |
| **📧 Gmail** | Leer bandeja de entrada, enviar correos, buscar mensajes, administrar borradores. |
| **📁 Google Drive** | Listar archivos, buscar, subir, descargar, organizar. |
| **🔔 Recordatorios** | Recordatorios únicos y recurrentes (diario, semanal, días específicos). Persisten tras reinicios vía Windows Task Scheduler. |
| **🤖 Telegram Bot** | Control remoto desde tu celular — envía comandos y recibe respuestas desde cualquier lugar. |
| **🖥️ Control del PC** | Volumen, brillo, abrir/cerrar apps, administrar ventanas, atajos de teclado, apagar, reiniciar, bloquear pantalla. |
| **⌨️ Escribir en Pantalla** | Dile a JARVIS que escriba cualquier cosa — simula entrada de teclado en cualquier campo de texto. |
| **🌤️ Clima** | Reportes del clima en tiempo real, pronósticos y alertas. |
| **🌐 Búsqueda Web** | Búsqueda y recuperación de información de internet. |
| **🎬 YouTube** | Reproducir videos, buscar, obtener contenido trending. |
| **📸 Análisis de Pantalla** | Captura la pantalla o webcam y haz preguntas sobre lo que ves. |
| **🎨 UI Cyberpunk** | Visualización Arc Reactor con 160 partículas, anillos holográficos rotatorios, soundwave reactiva y telemetría HUD en vivo. |

---

## 🏗️ Arquitectura

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
│  YouTube            ...y más                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Modelo de Concurrencia

JARVIS usa **asyncio** con 5 tareas paralelas bajo un `asyncio.TaskGroup`:
- `_listen_audio` — captura el micrófono
- `_send_realtime` — envía audio a Gemini
- `_receive_audio` — recibe respuestas de IA y llamadas a herramientas
- `_play_audio` — reproduce respuestas de audio
- `_watch_reconnect` — reconexión automática ante cambios de configuración

Cada tarea tiene **aislamiento de errores** — una falla transitoria en una tarea no destruye la sesión completa.

---

## 🛠️ Stack Tecnológico

| Tecnología | Propósito |
|-----------|-----------|
| **Python 3.12+** | Lenguaje principal |
| **Google Gemini Live API** (`genai`) | IA de voz en tiempo real con streaming bidireccional |
| **sounddevice** | Captura y reproducción de audio |
| **numpy** | Procesamiento de señal y amplificación de ganancia |
| **Tkinter** | UI Cyberpunk Arc Reactor personalizada |
| **pywinauto** | Automatización de GUI de Windows (WhatsApp, teclado) |
| **pyautogui** | Simulación de teclado y captura de pantalla |
| **spotipy** | Integración con Spotify Web API |
| **Google APIs** (Calendar, Gmail, Drive) | Suite de productividad en la nube |
| **python-telegram-bot** | Control remoto vía Telegram |
| **pycaw** | Control de volumen de sesiones de audio en Windows |
| **Pillow + opencv-python** | Captura y procesamiento de imágenes/pantalla |
| **requests, httpx, aiohttp** | Clientes HTTP |

---

## 📋 Requisitos Previos

- **Windows 10/11**
- **Python 3.12+**
- **Git**
- **Google Gemini API key** ([Obtén una aquí](https://aistudio.google.com/))
- **Spotify Premium** (para búsqueda y reproducción)
- **Telegram Bot Token** (opcional, para control remoto)

---

## 🔧 Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Jonas26-hash/JARVIS-AI-Asistente-de-Voz-con-Inteligencia-Artificial-en-Tiempo-Real.git
cd JARVIS-AI-Asistente-de-Voz-con-Inteligencia-Artificial-en-Tiempo-Real

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API keys (ver siguiente sección)
```

---

## ⚙️ Configuración

Copia `config/api_keys.example.json` a `config/api_keys.json` y completa tus claves:

```json
{
  "gemini_api_key": "TU_GEMINI_API_KEY",
  "spotify_client_id": "TU_SPOTIFY_CLIENT_ID",
  "spotify_client_secret": "TU_SPOTIFY_CLIENT_SECRET",
  "telegram_bot_token": "TU_TELEGRAM_BOT_TOKEN",
  "tmdb_api_key": "TU_TMDB_API_KEY",
  "timezone": "America/Lima",
  "language": "es",
  "location_city": "Lima",
  "mic_device": 1,
  "spk_device": 1
}
```

> **Nota:** `api_keys.json` está en `.gitignore` y **no** se subirá al repositorio. Tus claves se quedan en tu máquina.

---

## �️ Uso

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Ejecutar JARVIS
python main.py
```

Habla con naturalidad a JARVIS:

| Tú dices | JARVIS hace |
|----------|-------------|
| *"Abre WhatsApp y mándale un mensaje a mamá que llego en 10 minutos"* | Abre WhatsApp, busca el contacto, escribe y envía el mensaje |
| *"Pon música de Queen"* | Busca en Spotify y comienza a reproducir Queen |
| *"Recuérdame a las 7 PM llamar al médico"* | Crea un recordatorio persistente con Task Scheduler |
| *"¿Qué recordatorios tengo?"* | Lista todos los recordatorios pendientes con el tiempo restante |
| *"Escribe en el bloc de notas: lista de compras"* | Escribe texto en pantalla mediante simulación de teclado |
| *"Baja el volumen al 30%"* | Ajusta el volumen del sistema |
| *"¿Qué clima hace mañana?"* | Obtiene el pronóstico del clima |

---

## 🧰 Herramientas Disponibles

| Herramienta | Descripción |
|-------------|-------------|
| `whatsapp` | Enviar mensajes, abrir chats, administrar WhatsApp Desktop |
| `spotify_control` | Reproducir, pausar, saltar, buscar, reproducir playlists, volumen |
| `reminder` | Crear/listar/eliminar recordatorios únicos o recurrentes |
| `type_writer` | Escribir texto en pantalla mediante teclado simulado |
| `send_message` | Mensajería multiplataforma (WhatsApp, Telegram, SMS) |
| `weather_report` | Clima actual y pronósticos |
| `web_search` | Búsqueda en internet y recuperación de información |
| `youtube_video` | Reproducir, buscar, videos trending de YouTube |
| `google_calendar` | Listar, crear, editar, eliminar eventos del calendario |
| `gmail_control` | Leer, enviar, buscar correos electrónicos |
| `google_drive` | Listar, buscar, subir archivos |
| `computer_settings` | Volumen, brillo, modo oscuro, WiFi, apagado |
| `computer_control` | Clic, teclear, atajos, mouse, scroll, capturas |
| `desktop_control` | Fondo de pantalla, organizar escritorio, estadísticas del sistema |
| `browser_control` | Navegar, buscar, llenar formularios, administrar pestañas |
| `screen_process` | Capturar y analizar pantalla/webcam con visión IA |
| `telegram_bot` | Control remoto vía Telegram |
| `rgb_control` | Control de iluminación RGB |
| `game_updater` | Gestión de actualizaciones de juegos |
| `file_processor` | Operaciones y procesamiento de archivos |
| `flight_finder` | Búsqueda y seguimiento de vuelos |
| `accessibility` | Funciones de accesibilidad y lectura de pantalla |
| `news` | Últimas noticias |

---

## 📁 Estructura del Proyecto

```
JARVIS/
├── main.py                    # Punto de entrada — ciclo de vida de sesión, despacho de herramientas
├── ui.py                      # UI Cyberpunk Arc Reactor (Tkinter)
├── beta_config.py             # Gestión y rotación de API keys
├── core/
│   ├── prompt.txt             # System prompt para Gemini
│   ├── sounds.py              # Sonidos de feedback
│   └── ...
├── actions/
│   ├── whatsapp.py            # Automatización de WhatsApp
│   ├── spotify_control.py     # Spotify teclas multimedia + API
│   ├── reminder.py            # Recordatorios persistentes
│   ├── type_writer.py         # Herramienta de escritura por teclado
│   ├── google_calendar.py     # Integración con Google Calendar
│   ├── gmail_control.py       # Integración con Gmail
│   ├── weather_report.py      # Pronósticos del clima
│   ├── browser_control.pyc    # Automatización del navegador
│   ├── computer_control.pyc   # Control directo del PC
│   └── ... (más de 30 módulos de acción)
├── memory/
│   ├── memory_manager.pyc     # Gestión de memoria a largo plazo
│   └── long_term.json         # Almacenamiento de memoria persistente
├── config/
│   ├── api_keys.example.json  # Plantilla de API keys (segura para commits)
│   └── api_keys.json          # ⚠️ Tus claves reales (ignorado por git)
├── .gitignore
└── README.md
```

> **Nota:** Algunos módulos se distribuyen como `.pyc` (bytecode compilado) por optimización. Los fuentes equivalentes se publicarán conforme sean refactorizados.

---

## 🎨 Vista Previa de la UI

La interfaz Cyberpunk Arc Reactor incluye:
- **Partículas en vórtice** (160 partículas con estelas mejoradas)
- **Anillos holográficos rotatorios**
- **Soundwave reactiva** que pulsa con tu voz
- **Telemetría HUD brillante** (estado de conexión, niveles de audio, hora del sistema)
- **Núcleo de energía central** con brillo pulsante

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Siéntete libre de:
1. Hacer fork del repositorio
2. Crear una rama de funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Hacer commit de tus cambios
4. Hacer push a la rama
5. Abrir un Pull Request

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT — consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- **Google Gemini** por la innovadora Live API
- La **comunidad Python** por el increíble ecosistema de librerías
- **Tú** — por visitar este proyecto

---

<p align="center">
  Hecho con ❤️ por <a href="https://github.com/Jonas26-hash">Jonas26-hash</a>
</p>
