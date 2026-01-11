# CHANGELOG

## [Unreleased]

### Added - Video Voice Clone Feature 🎬

**Major new feature**: Create voice profiles from video files

#### Features
- **Video Upload**: Support for MP4, MOV, WebM formats (up to 100MB, 5 minutes)
- **Interactive Trimming**: Select specific 3-30 second segments for voice extraction
- **Audio Extraction**: Automatic conversion to 24kHz mono WAV using ffmpeg
- **Quality Validation**: Silence detection and audio quality checks
- **Consent System**: Required checkbox with ethics warning before voice cloning
- **Profile Management**: Voice metadata storage with creation date, source info, notes
- **Test Synthesis**: Built-in voice testing after profile creation
- **Full Integration**: New voices automatically appear in main TTS voice selector

#### Technical Details
- New `app/video/processor.py` module for video/audio processing
- Extended `ChatterboxEngine` with `create_voice_from_video()` method
- Voice metadata stored in `data/voice_metadata.json`
- Configurable limits via `config.toml`[video_voice_clone]` section
- Dependencies: `ffmpeg-python`, `librosa`

#### UI Enhancements
- New "🎬 Video Voice Clone" tab in main interface
- Step-by-step workflow: Upload → Trim → Consent → Create → Test
- Real-time duration display
- Progress indicators for long operations
- Comprehensive error messages

#### Documentation
- User guide: `docs/VIDEO_VOICE_CLONE.md`
- Configuration examples
- FFmpeg installation instructions
- Security best practices
- Troubleshooting guide

#### Safety & Ethics
- Required consent checkbox cannot be bypassed
- Clear warnings about voice cloning misuse
- Audit logging of all voice creation attempts
- Temporary file cleanup
- Local processing (no cloud upload)

---

## [0.3.0] - 2026-01-11

### Added - 10 UI/UX Enhancements

- Generation history with clickable replay (last 10 items)
- Voice metadata display (duration, size, date added)
- Text preprocessing options (remove URLs, special characters)
- Real-time character/word counter with duration estimate
- Color-coded text length warnings
- 5 built-in text presets/templates
- Copy-to-clipboard for output file paths
- Keyboard shortcut: Ctrl/Cmd+Enter to generate
- Progress indicators during synthesis and recording
- Engine status badge showing TTS provider and device

### Fixed - Comprehensive Bug Sweep

- Specific exception handling (no more blanket `except Exception`)
- File existence validation before operations
- Duplicate voice name detection with overwrite warnings
- Better error messages with actionable context
- Input sanitization for voice names and file paths
- Safer fallback audio generation with error recovery
- Added logging for all failed operations

### Changed

- Created `app/utils.py` for shared utility functions
- Improved error handling throughout codebase
- Better separation of concerns in engine code

---

## [0.2.0] - 2026-01-11

### Added - Documentation & Critical Bug Fixes  

- Comprehensive README.md with setup and usage instructions
- API documentation (`docs/API.md`)
- Usage guide (`docs/USAGE.md`)
- Configuration example file (`config.example.toml`)

### Fixed

- Removed duplicate `add_voice` method in engine
- Normalized default voice name ("default" vs "Chatterbox Default")
- Added `.gitkeep` files for empty directories
- Added `get_engine_status()` method for debugging
- UI status badge showing provider and device info

---

## [0.1.0] - 2026-01-10

### Added - Initial Release

- Text-to-speech generation with Chatterbox engine
- Voice cloning from audio samples
- Recording interface for custom voices
- Gradio web UI with "Starsilk" dark theme
- Desktop app launcher (macOS)
- Fallback audio generation mode
- Voice library management
- Audio file output
- Basic error handling and logging

### Technical

- `ChatterboxEngine` core audio system
- Voice profile storage in `data/voices/`
- Output files in `data/outputs/`
- Tkinter-based controller app
- PyWebView desktop integration
