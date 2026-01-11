# Usage Guide

## Getting Started

### First Launch

1. Start DexTalker using one of the methods:
   ```bash
   python run.py                 # Web UI only
   python app/launcher.py        # Full controller
   python app/desktop_app.py     # Desktop window
   ```

2. Wait for the status message: `✅ Status: Online (http://localhost:7860)`

3. Access the interface in your browser or desktop window

---

## Generating Speech

### Basic Usage

1. Navigate to the **Studio** tab
2. Enter your text in the **Input Text** field
3. Select a voice from the **Voice** dropdown
4. Click **Generate Speech**
5. Wait for the status to show `✅ Ready: <filename>`
6. The audio player will display the generated file

**Example Text**:
```
Welcome to DexTalker. The stars are silent, but we are not.
```

### Tips for Better Results

- **Punctuation**: Use proper punctuation for natural pauses
- **Length**: Longer texts may take more time to generate
- **Voice Selection**: Experiment with different voices for various tones
- **Special Characters**: Avoid excessive special characters or emojis

---

## Voice Cloning

### Recording a Voice Sample

1. Go to the **Voices** tab
2. In the **Record Sample** section:
   - Set **Recording Length** (2-20 seconds, 6 recommended)
   - Click **Record Sample**
   - Speak clearly into your microphone
3. Preview the recording in the **Recorded Sample** player
4. If unsatisfied, record again

**Recording Tips**:
- Use a quiet environment
- Speak clearly and naturally
- Include varied intonation
- Avoid background noise
- 6-10 seconds is optimal

### Uploading an Existing Sample

1. In the **Upload Sample** section:
   - Click **Browse** or drag a `.wav` file
   - Upload completes automatically
2. The file appears in the upload field

**File Requirements**:
- Format: `.wav` only
- Quality: Higher is better (44100 Hz recommended)
- Duration: 6-10 seconds ideal

### Registering the Voice

1. Enter a **Voice Name** (e.g., "Morgan Freeman")
2. Ensure either:
   - A recorded sample exists, OR
   - An uploaded file is selected
3. Click **Register Voice**
4. Wait for confirmation: `✅ Voice registered: <name>`

The new voice will appear in:
- The **Studio** tab voice dropdown
- The **Available Voices** manifest

---

## Managing Voices

### Viewing Available Voices

The **Available Voices** panel displays all registered voices in JSON format:

```json
["Albert", "Aman", "Bad News", "Bubbles", "Daniel", "MyCustomVoice"]
```

### Refreshing the Voice List

Click the **Refresh Voices** button to reload the list after:
- Manually adding files to `data/voices/`
- Deleting voice files
- Having multiple windows open

### Removing Voices

To remove a voice:
1. Close DexTalker
2. Navigate to `data/voices/`
3. Delete the unwanted `.wav` file
4. Restart DexTalker

---

## Output Files

### Locating Generated Audio

All generated speech files are saved to:
```
data/outputs/
```

Files are named:
```
tts_YYYYMMDD_HHMMSS_<uuid>.wav
```

Example:
```
tts_20260110_194040_86d04816.wav
```

### Playing Saved Files

You can:
- **Play in DexTalker**: Files appear in the Studio output player
- **Open Externally**: Use Finder or any audio player
- **Share**: Copy files to other locations

### Managing Storage

To clear old files:
```bash
rm data/outputs/*.wav
```

Or manually delete from Finder.

---

## Using the Launcher

The **DexTalker Controller** provides easy management:

### Buttons

- **🚀 Launch UI**: Opens web browser to `http://localhost:7860`
- **🖥 Desktop Window**: Opens native desktop app window
- **🛑 Shut Down**: Stops all services and closes the launcher

### Status Indicator

Watch the status label for:
- `Ready to launch` – Not yet started
- `Initializing Chatterbox...` – Starting up
- `Online (http://localhost:7860)` – Ready to use
- `Failed to start` – Check `launcher.log` for errors

---

## Troubleshooting

### Port Already in Use

If you see:
```
Port 7860 already in use
```

**Solution**:
1. Close any running DexTalker instances
2. Or run the launcher's **Clean Ports** function (automatic on startup)

### No Microphone Access

If recording fails:

**macOS**:
1. Go to **System Preferences → Security & Privacy → Microphone**
2. Grant permission to Terminal or Python
3. Restart DexTalker

### Voice Not Generating

**Checklist**:
- Is the voice selected in the dropdown?
- Is there text in the input field?
- Check `dextalker.log` for errors
- Try the "default" voice to test the engine

### Desktop Window Not Opening

Ensure `pywebview` is installed:
```bash
pip install pywebview
```

For macOS-specific issues, check `desktop_app_run.log`.

---

## Advanced Usage

### Custom Python Integration

```python
import asyncio
from app.engine.chatterbox import ChatterboxEngine

async def main():
    engine = ChatterboxEngine()
    await engine.initialize()
    
    # Generate speech
    file, status = await engine.synthesize(
        "This is a test.",
        voice_id="Albert"
    )
    
    print(f"Generated: {file}")

asyncio.run(main())
```

### Environment Variables

- `DEXTALKER_PORT`: Override default port (7860)

Example:
```bash
export DEXTALKER_PORT=8000
python run.py
```

---

## Keyboard Shortcuts

### Web Interface

- **Tab**: Navigate between fields
- **Enter**: Submit forms (when focused)

### Desktop App

- **⌘+W**: Close window (stops desktop app only)
- **⌘+Q**: Quit (if applicable)

---

## Best Practices

1. **Voice Samples**: Use high-quality recordings for best cloning results
2. **Text Input**: Keep individual generations under 500 words for speed
3. **File Management**: Periodically clear old outputs to save space
4. **Updates**: Pull latest changes from GitHub regularly
5. **Backups**: Save important voice samples externally

---

For more information, see:
- [API Documentation](API.md)
- [README](../README.md)
- [GitHub Issues](https://github.com/westkitty/DexTalker/issues)
