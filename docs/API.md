# API Documentation

## ChatterboxEngine

The `ChatterboxEngine` class is the core audio processing system for DexTalker.

### Initialization

```python
from app.engine.chatterbox import ChatterboxEngine

engine = ChatterboxEngine(data_dir="data")
await engine.initialize()
```

**Parameters**:
- `data_dir` (str, optional): Path to data directory. Default: `"data"`

### Methods

#### `synthesize(text, voice_id)`

Generate speech from text.

**Parameters**:
- `text` (str): Input text to synthesize
- `voice_id` (str): Voice identifier (e.g., "Albert", "default")

**Returns**:
- `Tuple[Optional[str], str]`: (Path to audio file, Status message)

**Example**:
```python
file_path, status = await engine.synthesize(
    "Hello, world!", 
    voice_id="Albert"
)
```

---

#### `add_voice(voice_name, voice_file)`

Register a new voice from an audio file.

**Parameters**:
- `voice_name` (str): Display name for the voice
- `voice_file` (str): Path to .wav file

**Returns**:
- `Tuple[bool, str]`: (Success status, Message)

**Example**:
```python
success, msg = await engine.add_voice(
    "CustomVoice", 
    "/path/to/sample.wav"
)
```

---

#### `record_voice_sample(duration_sec, sample_rate)`

Record audio from the system microphone.

**Parameters**:
- `duration_sec` (float, optional): Recording duration. Default: `5.0`
- `sample_rate` (int, optional): Sample rate in Hz. Default: `44100`

**Returns**:
- `Tuple[Optional[str], str]`: (Path to recorded file, Status message)

**Example**:
```python
path, status = await engine.record_voice_sample(duration_sec=6.0)
```

---

#### `get_available_voices()`

Get list of all registered voices.

**Returns**:
- `List[str]`: List of voice identifiers

**Example**:
```python
voices = engine.get_available_voices()
# Returns: ["Albert", "Aman", "Bad News", "Bubbles", "Daniel"]
```

---

#### `get_output_directory()`

Get the path to the output directory.

**Returns**:
- `Path`: Output directory path object

---

## Gradio Interface Handlers

### `synthesize_handler(text, voice)`

Gradio callback for text-to-speech generation.

**Parameters**:
- `text` (str): Input text
- `voice` (str): Selected voice name

**Returns**:
- `Tuple[Optional[str], str]`: (Audio file path, Status message)

---

### `add_voice_handler(voice_name, voice_upload, recorded_path)`

Gradio callback for adding new voices.

**Parameters**:
- `voice_name` (str): Name for the new voice
- `voice_upload` (str): Uploaded file path (optional)
- `recorded_path` (str): Recorded sample path (optional)

**Returns**:
- `Tuple[str, gr.update, List[str]]`: (Status message, Voice dropdown update, Voice list)

---

### `record_voice_handler(duration_sec)`

Gradio callback for recording voice samples.

**Parameters**:
- `duration_sec` (float): Recording duration in seconds

**Returns**:
- `Tuple[Optional[str], str]`: (Recorded file path, Status message)

---

### `refresh_voices_handler()`

Refresh the list of available voices.

**Returns**:
- `Tuple[gr.update, List[str]]`: (Voice dropdown update, Updated voice list)

---

## Data Formats

### Voice Files
- **Format**: WAV (uncompressed)
- **Sample Rate**: 44100 Hz recommended
- **Channels**: Mono or Stereo
- **Bit Depth**: 16-bit recommended
- **Duration**: 6-10 seconds for best results

### Output Files
- **Format**: WAV
- **Naming**: `tts_YYYYMMDD_HHMMSS_<uuid>.wav`
- **Location**: `data/outputs/`

---

## Error Handling

All async methods return tuples with status messages. Check the second element for error information:

```python
file_path, status = await engine.synthesize("test", "Albert")

if file_path:
    print(f"Success: {file_path}")
else:
    print(f"Error: {status}")
```

---

## Thread Safety

The `ChatterboxEngine` uses:
- Thread locks for voice library access
- Asyncio event loops for concurrent operations
- Thread pools for blocking I/O operations

All public methods are async-safe and can be called from Gradio callbacks.
