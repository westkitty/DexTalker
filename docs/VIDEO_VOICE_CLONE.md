# Video Voice Clone Feature

## Overview

The Video Voice Clone feature allows you to create custom voice profiles from video files. Upload a video, select a speech segment, and DexTalker will extract the audio and create a voice profile you can use for text-to-speech generation.

---

## How to Use

### Step 1: Upload Video

1. Navigate to the **🎬 Video Voice Clone** tab
2. Click the video upload area
3. Select a video file (MP4, MOV, or WebM format)
4. Maximum file size: **100MB**
5. Maximum duration: **5 minutes** (300 seconds)

The system will automatically display video information after upload.

---

### Step 2: Trim Segment

Select the portion of video containing clear, high-quality speech:

- **Start Time**: Enter the start time in seconds (e.g., `5.5`)
- **End Time**: Enter the end time in seconds (e.g., `15.8`)
- **Duration**: Must be between **3-30 seconds**

**Tips for best results**:
- Select segments with minimal background noise
- Ensure clear, uninterrupted speech
- Avoid music or overlapping voices
- Choose segments where the speaker's voice is consistent

---

### Step 3: Consent & Profile Details

#### Ethics & Consent ⚠️

**IMPORTANT**: You must have explicit rights/consent to use the voice:
- Own consent for your own voice ✅
- Written permission from the person ✅
- Public domain/licensed content ✅
- Public figures without permission ❌
- Other people without consent ❌
- Fraudulent purposes ❌

#### Required Check

✅ Check: **"I confirm I have the rights and consent to use this voice"**

Without this confirmation, voice profile creation will be blocked.

#### Profile Information

- **Voice Profile Name**: Choose a descriptive name (e.g., "John Professional", "Mary Interview")
  - Only letters, numbers, hyphens, and underscores allowed
  - Unique names recommended
  
- **Notes (optional)**: Add context about the voice
  - Example: "Source: TEDx talk 2024"
  - Example: "Character: Documentary narrator"

---

### Step 4: Create Profile

Click **✨ Create Voice Profile**

The system will:
1. ✓ Validate video format and size
2. ✓ Extract audio from the trimmed segment
3. ✓ Convert to 24kHz mono WAV
4. ✓ Analyze audio quality (silence check, RMS energy)
5. ✓ Save voice profile with metadata
6. ✓ Make available in voice selector

**Processing time**: Typically 5-15 seconds

---

### Step 5: Test Voice

After successful creation:

1. Enter test text in the **Test Text** box
2. Click **🎙️ Test Voice**
3. Listen to the generated audio
4. Verify the voice quality matches expectations

If satisfied, the voice is ready to use in the **Studio** tab!

---

## Technical Details

### System Requirements

**Required**:
- `ffmpeg` installed on system ([Installation Guide](#ffmpeg-installation))
- Python packages: `ffmpeg-python`, `librosa`, `soundfile`

**Check dependencies**:
```bash
ffmpeg -version  # Should show ffmpeg version
pip list | grep ffmpeg-python  # Should be installed
```

### Audio Processing Specifications

- **Sample Rate**: 24,000 Hz (24kHz)
- **Channels**: Mono (1 channel)
- **Format**: 16-bit PCM WAV
- **Normalization**: Automatic

### File Limits & Configuration

Default limits (configurable in `config.toml`):

```toml
[video_voice_clone]
max_upload_size_mb = 100
max_video_duration_sec = 300
min_audio_duration_sec = 3
max_audio_duration_sec = 30
target_sample_rate = 24000
target_channels = 1
```

---

## Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "File size exceeds limit" | Video > 100MB | Compress video or trim before upload |
| "Video duration exceeds limit" | Video > 5 minutes | Cut video to under 5 minutes |
| "Segment too short" | Less than 3 seconds | Select longer segment |
| "Audio appears silent" | Low audio levels | Choose segment with clear speech |
| "Consent required" | Checkbox not checked | Check consent checkbox |
| "FFmpeg error" | ffmpeg not installed | Install ffmpeg (see below) |
| "Format not supported" | Wrong codec | Use MP4/H.264 or convert |

---

## FFmpeg Installation

### macOS
```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows
Download from: https://ffmpeg.org/download.html

Verify installation:
```bash
ffmpeg -version
```

---

## Best Practices

### Recording Quality

✅ **Do**:
- Use high-quality source videos (1080p+)
- Ensure audio bitrate is adequate (128kbps+)
- Record in quiet environment
- Use external microphone if possible
- Keep consistent volume

❌ **Don't**:
- Use heavily compressed videos
- Include background music/noise
- Use distorted or clipped audio
- Mix multiple speakers in segment

### Voice Selection

**Good segments**:
- Clear pronunciation
- Consistent tone
- Minimal background noise
- Natural speaking pace
- 6-10 seconds of speech

**Poor segments**:
- Whispering or shouting
- Heavy accent changes
- Music overlays
- Echo/reverb
- Wind noise

---

## Security & Privacy

### Data Storage

- **Videos**: Temporary, deleted after processing
- **Audio**: Saved to `data/voices/<name>.wav`
- **Metadata**: Stored in `data/voice_metadata.json`

### Safe Practices

1. **Never upload sensitive videos** containing:
   - Private conversations
   - Confidential information
   - Protected content

2. **Respect intellectual property**:
   - Don't clone copyrighted characters
   - Obtain licenses for commercial use
   - Follow fair use guidelines

3. **Audit trail**:
   - All voice creations logged with timestamp
   - Metadata includes source file name
   - Notes field for documentation

---

## Troubleshooting

### Video won't upload

- Check file format (MP4, MOV, WebM only)
- Verify file size < 100MB
- Ensure video isn't corrupted
- Try converting to MP4/H.264

### Audio extraction fails

- Verify ffmpeg is installed correctly
- Check video has audio track
- Try different trim range
- Inspect `dextalker.log` for details

### Voice quality poor

- Select clearer speech segment
- Avoid segments with echo
- Use higher quality source video
- Try longer segment (8-10 seconds)

### Voice not appearing in selector

- Click "🔄 Refresh Voices" in Voices tab
- Check `data/voices/` directory
- Verify no special characters in name
- Check logs for errors

---

## Advanced Usage

### Custom Configuration

Edit `config.toml`:

```toml
[video_voice_clone]
# Allow larger files
max_upload_size_mb = 200

# Allow longer videos
max_video_duration_sec = 600

# Require longer voice samples
min_audio_duration_sec = 5
max_audio_duration_sec = 60

# Use different sample rate
target_sample_rate = 16000
```

### Metadata Access

Voice metadata is stored in JSON format:

```bash
cat data/voice_metadata.json
```

Example entry:
```json
{
  "John_Professional": {
    "source_type": "video",
    "source_file": "interview.mp4",
    "trim_range": [23.5, 32.8],
    "duration_sec": 9.3,
    "sample_rate": 24000,
    "created_date": "2026-01-11T06:45:00",
    "notes": "TEDx presentation excerpt",
    "audio_file": "data/voices/John_Professional.wav"
  }
}
```

---

## FAQ

**Q: Can I use YouTube videos?**  
A: Only if you have explicit permission from the creator and comply with YouTube's Terms of Service.

**Q: How many voice profiles can I create?**  
A: Unlimited, but each takes disk space (~200KB-2MB per voice).

**Q: Can I delete voice profiles?**  
A: Yes, manually delete from `data/voices/` directory or use the file manager.

**Q: Does this work offline?**  
A: Yes, once dependencies are installed, no internet required.

**Q: What about video privacy?**  
A: Videos are processed locally and deleted after extraction. No cloud upload.

**Q: Can I use this commercially?**  
A: Depends on your source video license and local laws. Consult legal advice.

---

## Support

For issues or questions:
1. Check `dextalker.log` for error details
2. Review this documentation
3. Open an issue: https://github.com/westkitty/DexTalker/issues

**Include in bug reports**:
- Error message
- Video format/size
- Steps to reproduce
- Log excerpt
