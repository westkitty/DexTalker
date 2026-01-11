# 🎙️ DexTalker

**A Modern Text-to-Speech Application with Voice Cloning**

DexTalker is a sleek, reliable TTS application built with Gradio and powered by the Chatterbox engine. Create natural-sounding speech from text, clone voices, and manage your audio library—all with a premium "Starsilk" UI aesthetic.

---

## ✨ Features

- **🗣️ Text-to-Speech Generation**: Convert text to natural speech using multiple voice profiles
- **🎤 Voice Cloning**: Record or upload custom voice samples to create unique voices
- **🎨 Starsilk UI**: Premium dark theme with smooth gradients and modern design
- **💻 Multiple Interfaces**: Web UI, Desktop App, and Launcher with controller
- **📁 Voice Management**: Add, organize, and manage voice profiles easily
- **🔊 Audio Playback**: Instant playback of generated speech

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.8 or higher
- **macOS**: Required for desktop app features (optional for web UI)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/westkitty/DexTalker.git
   cd DexTalker
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run DexTalker**:
   ```bash
   python run.py
   ```

   The web UI will be available at **http://localhost:7860**

---

## 📖 Usage

### Web Interface

Launch the web UI for browser-based access:
```bash
python run.py
```

Navigate to `http://localhost:7860` in your browser.

### Desktop Application

Launch the native desktop window:
```bash
python app/desktop_app.py
```

### Controller Launcher

Use the Tkinter-based controller for easy management:
```bash
python app/launcher.py
```

The controller provides buttons to:
- 🚀 **Launch UI**: Opens web interface in your browser
- 🖥 **Desktop Window**: Launches native desktop app
- 🛑 **Shut Down**: Cleanly stops all services

---

## 🎨 Interface Overview

### Studio Tab
- **Generator Panel**: Enter text and select a voice to generate speech
- **Output**: Audio player for generated files
- **Status Indicator**: Real-time feedback on generation progress

### Voices Tab
- **Record Sample**: Capture voice samples using your microphone (2-20 seconds)
- **Upload Sample**: Upload existing .wav files for voice cloning
- **Register Voice**: Add custom voices to your library
- **Voice Manifest**: View all available voices in JSON format

---

## 🔧 Configuration

### Voice Files
- Voice samples are stored in `data/voices/`
- Supported format: `.wav` files
- Recommended: 6-10 seconds of clear speech
- Sample voices included: Albert, Aman, Bad News, Bubbles, Daniel

### Output Directory
- Generated audio saves to `data/outputs/`
- Files named: `tts_YYYYMMDD_HHMMSS_<uuid>.wav`

### Logs
- Application log: `dextalker.log`
- Launcher log: `launcher.log`
- Desktop app log: `desktop_app_run.log`

---

## 📁 Project Structure

```
DexTalker/
├── app/
│   ├── engine/
│   │   └── chatterbox.py      # Core TTS engine
│   ├── ui/
│   │   └── main.py            # Gradio web interface
│   ├── desktop_app.py         # Native desktop wrapper
│   └── launcher.py            # Tkinter controller
├── data/
│   ├── voices/                # Voice samples library
│   ├── outputs/               # Generated audio files
│   └── models/                # (Reserved for future models)
├── scripts/
│   ├── create_dextalker_app.sh
│   ├── verify_dextalker.py
│   └── verify_engine.py
├── run.py                     # Main entry point
└── requirements.txt           # Python dependencies
```

---

## 🛠️ Development

### Running Tests

Verify the engine:
```bash
python scripts/verify_engine.py
```

Verify the full application:
```bash
python scripts/verify_dextalker.py
```

### Building macOS App

Create a standalone `.app` bundle:
```bash
bash scripts/create_dextalker_app.sh
```

---

## 🎯 Roadmap

- [ ] Additional TTS engine backends
- [ ] Real-time streaming synthesis
- [ ] Advanced voice tuning controls
- [ ] Batch processing
- [ ] Export to multiple formats (MP3, OGG, etc.)
- [ ] Voice effect presets

---

## 📄 License

This project is open-source and available for personal and commercial use.

---

## 🙏 Acknowledgments

- **Chatterbox TTS**: Core text-to-speech engine
- **Gradio**: Web UI framework
- **PyWebView**: Native desktop integration

---

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub:
**https://github.com/westkitty/DexTalker/issues**

---

**Made with 🎙️ by the DexTalker team**
