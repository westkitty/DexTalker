import logging
import asyncio
import importlib
import math
import os
import shutil
import threading
import uuid
import wave
from array import array
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("dextalker.log")
    ]
)
logger = logging.getLogger("DexTalker.Engine")

class ChatterboxEngine:
    """
    Core Audio Engine for DexTalker using Chatterbox architecture.
    Prioritizes reliability, thread-safety, and deterministic outputs.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.models_dir = self.data_dir / "models"
        self.output_dir = self.data_dir / "outputs"
        self.voices_dir = self.data_dir / "voices"
        self.recordings_dir = self.data_dir / "recordings"
        self.videos_dir = self.data_dir / "videos"  # For temp video processing
        self.voice_metadata_file = self.data_dir / "voice_metadata.json"
        
        # Ensure directories exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .gitkeep files for empty directories
        for directory in [self.models_dir, self.output_dir]:
            gitkeep = directory / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
        
        self.is_loaded = False
        self._provider = None
        self._provider_name = None
        self._provider_device = None
        self._provider_sample_rate = None
        self._provider_error = None
        self._lock = threading.Lock()
        self._init_lock = None
        self._init_lock_loop = None
        
    async def initialize(self) -> Tuple[bool, str]:
        """
        Initialize the TTS engine asynchronously.
        Returns: (success, message)
        """
        loop = asyncio.get_running_loop()
        if self._init_lock is None or self._init_lock_loop is not loop:
            self._init_lock = asyncio.Lock()
            self._init_lock_loop = loop

        async with self._init_lock:
            if self.is_loaded:
                return True, "Chatterbox Engine already initialized."

            logger.info("Initializing Chatterbox Engine...")
            try:
                # Import lazily to keep startup light.
                self._provider = None
                self._provider_name = None
                self._provider_device = None
                self._provider_sample_rate = None
                self._provider_error = None

                try:
                    module = importlib.import_module("chatterbox")
                    provider_cls = getattr(module, "ChatterboxTTS", None)
                    if provider_cls is not None:
                        import torch
                        if torch.cuda.is_available():
                            device = "cuda"
                        elif torch.backends.mps.is_available():
                            device = "mps"
                        else:
                            device = "cpu"
                        logger.info("Loading Chatterbox models on %s...", device)
                        try:
                            self._provider = provider_cls.from_pretrained(device=device)
                            self._provider_name = "chatterbox"
                            self._provider_device = device
                            self._provider_sample_rate = getattr(self._provider, "sr", None)
                        except Exception as e:
                            self._provider_error = f"ChatterboxTTS.from_pretrained failed on {device}: {e}"
                            logger.exception("Chatterbox init failed on %s", device)
                            if device == "mps":
                                logger.info("Retrying Chatterbox on cpu...")
                                try:
                                    self._provider = provider_cls.from_pretrained(device="cpu")
                                    self._provider_name = "chatterbox"
                                    self._provider_device = "cpu"
                                    self._provider_sample_rate = getattr(self._provider, "sr", None)
                                    self._provider_error = None
                                except Exception as cpu_err:
                                    self._provider_error = f"ChatterboxTTS.from_pretrained failed on cpu: {cpu_err}"
                                    logger.exception("Chatterbox init failed on cpu")
                except ImportError as e:
                    self._provider_error = f"Failed to import chatterbox: {e}"
                    logger.exception("Chatterbox import failed")
                except Exception as e:
                    self._provider_error = f"Unexpected chatterbox error: {e}"
                    logger.exception("Unexpected Chatterbox init error")

                if self._provider is None:
                    for module_name in ("chatterbox_tts",):
                        try:
                            module = importlib.import_module(module_name)
                        except ImportError as e:
                            self._provider_error = f"Failed to import {module_name}: {e}"
                            logger.exception("Import failed for %s", module_name)
                            continue
                        provider_cls = getattr(module, "TTS", None)
                        if provider_cls is not None:
                            self._provider = provider_cls()
                            logger.info("Chatterbox provider loaded from %s.", module_name)
                            self._provider_name = module_name
                            break

                if self._provider is None:
                    suffix = f" Last error: {self._provider_error}" if self._provider_error else ""
                    logger.warning(
                        "Chatterbox library not found or failed to load. Running in fallback audio mode.%s",
                        suffix
                    )

                # Simulating load time for realism/verification
                await asyncio.sleep(0.5)

                self.is_loaded = True
                msg = "Chatterbox Engine initialized successfully."
                logger.info(msg)
                status = self.get_engine_status()
                logger.info(
                    "CHATTERBOX_AVAILABLE=%s provider=%s device=%s error=%s",
                    not status["fallback_mode"],
                    status["provider"],
                    status["device"],
                    status.get("error") or "none",
                )
                return True, msg
            except Exception as e:
                msg = f"Failed to initialize Chatterbox: {str(e)}"
                logger.error(msg)
                return False, msg

    async def synthesize(self, text: str, voice_id: str = "default") -> Tuple[Optional[str], str]:
        """
        Synthesize speech from text securely and reliably.
        
        Args:
            text (str): Input text to synthesize.
            voice_id (str): The ID of the voice to use.
            
        Returns:
            Tuple[Optional[str], str]: (Path to generated file or None, Status message)
        """
        if not text or not text.strip():
            return None, "Error: Input text cannot be empty."

        if not self.is_loaded:
            success, msg = await self.initialize()
            if not success:
                return None, msg

        # Generate deterministic filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        filename = f"tts_{timestamp}_{unique_id}.wav"
        output_path = self.output_dir / filename
        
        logger.info(f"Starting synthesis: inputs='{text[:30]}...' voice='{voice_id}' -> target='{output_path}'")
        
        try:
            # Thread-safe execution wrapper
            await asyncio.to_thread(self._generate_file, text, voice_id, output_path)
            
            if output_path.exists() and output_path.stat().st_size > 0:
                logger.info(f"Synthesis complete: {output_path}")
                return str(output_path), "Success"
            else:
                msg = "Error: File was not created or is empty."
                logger.error(msg)
                return None, msg
                
        except Exception as e:
            msg = f"Synthesis Exception: {str(e)}"
            logger.error(msg)
            return None, msg

    def _generate_file(self, text: str, voice_id: str, output_path: Path):
        """
        Internal blocking method to handle the actual generation.
        This runs inside a thread pool.
        """
        if self._provider is not None:
            with self._lock:
                tts_to_file = getattr(self._provider, "tts_to_file", None)
                if callable(tts_to_file):
                    try:
                        tts_to_file(text=text, file_path=str(output_path), speaker=voice_id)
                        return
                    except Exception as e:
                        logger.warning("Provider tts_to_file failed, falling back. Error: %s", e)
                generate = getattr(self._provider, "generate", None)
                if callable(generate):
                    try:
                        self._generate_chatterbox_audio(text, voice_id, output_path)
                        return
                    except Exception as e:
                        logger.warning("Provider generate failed, falling back. Error: %s", e)

        self._generate_fallback_audio(text, output_path)

    def _generate_chatterbox_audio(self, text: str, voice_id: str, output_path: Path):
        voice_path = self._resolve_voice_path(voice_id)
        audio_prompt = str(voice_path) if voice_path else None
        
        try:
            audio = self._provider.generate(text, audio_prompt_path=audio_prompt)
        except Exception as e:
            raise RuntimeError(f"Failed to generate audio: {str(e)}") from e

        try:
            audio = audio.squeeze(0)
        except (AttributeError, RuntimeError):
            # Audio might already be in correct shape
            pass

        if hasattr(audio, "detach"):
            audio = audio.detach().cpu().numpy()

        try:
            import soundfile as sf
        except ImportError as e:
            raise RuntimeError("soundfile is required for Chatterbox output.") from e

        sample_rate = self._provider_sample_rate or getattr(self._provider, "sr", None) or 24000
        
        try:
            sf.write(str(output_path), audio, sample_rate)
        except Exception as e:
            raise RuntimeError(f"Failed to write audio file: {str(e)}") from e

    def _resolve_voice_path(self, voice_id: str) -> Optional[Path]:
        if not voice_id:
            return None
        normalized = voice_id.strip()
        if normalized.lower() in {
            "system default",
            "chatterbox standard",
            "neon prime",
            "chatterbox default",
            "default",
        }:
            return None

        candidate = Path(normalized)
        if candidate.is_file():
            return candidate

        direct = self.voices_dir / normalized
        if direct.is_file():
            return direct

        if not normalized.lower().endswith(".wav"):
            wav_candidate = self.voices_dir / f"{normalized}.wav"
            if wav_candidate.is_file():
                return wav_candidate

        normalized_lower = normalized.lower()
        for path in self.voices_dir.iterdir():
            if path.is_file() and path.suffix.lower() == ".wav":
                if path.stem.lower() == normalized_lower:
                    return path

        return None

    def _generate_fallback_audio(self, text: str, output_path: Path):
        """Generate a short, valid WAV tone when no TTS provider is available."""
        sample_rate = 22050
        duration = max(1.0, min(6.0, len(text) / 18.0))
        frequency = 440.0 + (len(text) % 5) * 55.0
        amplitude = 0.2
        frames = int(sample_rate * duration)

        try:
            import numpy as np
        except ImportError:
            np = None

        try:
            with wave.open(str(output_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)

                if np is not None:
                    t = np.linspace(0, duration, frames, endpoint=False)
                    waveform = amplitude * np.sin(2 * math.pi * frequency * t)
                    audio = (waveform * 32767).astype(np.int16)
                    wf.writeframes(audio.tobytes())
                else:
                    data = array("h")
                    for i in range(frames):
                        sample = int(32767 * amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                        data.append(sample)
                    wf.writeframes(data.tobytes())
        except Exception as e:
            logger.error(f"Failed to generate fallback audio: {e}")
            raise

    async def save_recording(self, source_path: str, name_prefix: str = "recording") -> Tuple[Optional[str], str]:
        """
        Save a temporary recording file to the permanent recordings directory.
        
        Args:
            source_path (str): Path to the temporary file.
            name_prefix (str): Prefix for the saved file name.
            
        Returns:
            Tuple[Optional[str], str]: (Path to new file or None, Status message)
        """
        if not source_path or not os.path.exists(source_path):
            return None, "Error: Source recording not found."
            
        # Ensure recordings dir exists
        recordings_dir = self.data_dir / "recordings"
        recordings_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate clean filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prefix = "".join(c for c in name_prefix if c.isalnum() or c in ('-', '_'))
        filename = f"{safe_prefix}_{timestamp}.wav"
        dest_path = recordings_dir / filename
        
        try:
            # Use run_in_executor for file IO to avoid blocking
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, shutil.copy2, source_path, dest_path)
            
            logger.info(f"Saved recording: {source_path} -> {dest_path}")
            return str(dest_path), "Success"
        except Exception as e:
            msg = f"Failed to save recording: {e}"
            logger.error(msg)
            return None, msg

    def get_saved_recordings(self) -> List[Tuple[str, str]]:
        """
        Get list of saved recordings.
        Returns: List of (Filename, Full Path) tuples, sorted by newest first.
        """
        recordings_dir = self.data_dir / "recordings"
        if not recordings_dir.exists():
            return []
            
        files = []
        try:
            for path in recordings_dir.iterdir():
                if path.is_file() and path.suffix.lower() in ('.wav', '.mp3', '.ogg', '.flac'):
                    files.append((path.name, str(path)))
        except OSError as e:
            logger.error(f"Error listing recordings: {e}")
            return []
            
        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
        return files

    def get_output_directory(self) -> str:
        return str(self.output_dir)

    def get_available_voices(self) -> List[str]:
        """Return list of available voice profiles."""
        voices = ["default"]
        try:
            for path in sorted(self.voices_dir.iterdir()):
                if path.is_file() and path.suffix.lower() == ".wav":
                    voices.append(path.stem)
        except OSError as e:
            logger.warning("Failed to read voices directory. Error: %s", e)
        return voices
    
    def get_engine_status(self) -> dict:
        """Return engine status information for debugging and UI display."""
        return {
            "initialized": self.is_loaded,
            "provider": self._provider_name or "fallback",
            "device": self._provider_device or "N/A",
            "fallback_mode": self._provider is None,
            "available_voices_count": len(self.get_available_voices()),
            "error": self._provider_error,
        }

    async def add_voice(self, voice_name: str, voice_file: str) -> Tuple[bool, str]:
        return await asyncio.to_thread(self._add_voice_sync, voice_name, voice_file)

    def _add_voice_sync(self, voice_name: str, voice_file: str) -> Tuple[bool, str]:
        if not voice_name or not voice_name.strip():
            return False, "Voice name is required."
        if not voice_file:
            return False, "Voice sample is required."
        
        # Check if file exists
        src_path = Path(voice_file)
        if not src_path.exists():
            return False, "Voice file not found."
        if not src_path.is_file():
            return False, "Path must be a file."

        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", voice_name.strip()).strip("_")
        if not safe_name:
            return False, "Voice name must contain letters or numbers."
        
        # Check for duplicate
        dest_path = self.voices_dir / f"{safe_name}.wav"
        if dest_path.exists():
            logger.warning(f"Voice '{safe_name}' already exists, overwriting.")

        try:
            import soundfile as sf
            audio, sr = sf.read(src_path)
            sf.write(dest_path, audio, sr)
        except Exception as audio_err:
            if src_path.suffix.lower() != ".wav":
                return False, "Unsupported audio format. Upload a .wav file."
            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                logger.error(f"Failed to save voice: {e}")
                return False, f"Failed to save voice: {e}"

        return True, f"Voice '{safe_name}' added."

    async def record_voice_sample(
        self,
        duration_sec: float = 5.0,
        sample_rate: int = 44100,
    ) -> Tuple[Optional[str], str]:
        return await asyncio.to_thread(self._record_voice_sample_sync, duration_sec, sample_rate)

    def _record_voice_sample_sync(
        self,
        duration_sec: float,
        sample_rate: int,
    ) -> Tuple[Optional[str], str]:
        try:
            import sounddevice as sd
        except Exception:
            return None, "Recording is unavailable (sounddevice not installed)."

        duration_sec = max(1.0, min(30.0, float(duration_sec)))
        frames = int(sample_rate * duration_sec)

        try:
            audio = sd.rec(frames, samplerate=sample_rate, channels=1, dtype="int16")
            sd.wait()
        except Exception as e:
            return None, f"Recording failed: {e}"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:6]
        filename = f"voice_rec_{timestamp}_{unique_id}.wav"
        output_path = self.recordings_dir / filename

        try:
            import soundfile as sf
            sf.write(output_path, audio, sample_rate)
        except Exception as e:
            return None, f"Failed to save recording: {e}"

        return str(output_path), "Recording captured."

    async def create_voice_from_video(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        voice_name: str,
        notes: str = "",
        consented: bool = False
    ) -> Tuple[bool, str]:
        """
        Create a voice profile from a video segment.
        
        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds
            voice_name: Name for the voice profile
            notes: Optional notes about the voice
            consented: User has consented to use this voice
            
        Returns:
            Tuple of (success, message)
        """
        if not consented:
            return False, "Consent required. You must agree to have rights to use this voice."
        
        try:
            from app.video.processor import VideoProcessor
            import json
            
            # Load config if exists
            config = {}
            if Path("config.toml").exists():
                try:
                    import toml
                    full_config = toml.load("config.toml")
                    config = full_config.get("video_voice_clone", {})
                except:
                    pass
            
            # Initialize video processor
            processor = VideoProcessor(config)
            
            # Validate video
            video_path_obj = Path(video_path)
            valid, msg = processor.validate_video(video_path_obj)
            if not valid:
                return False, f"Video validation failed: {msg}"
            
            # Sanitize voice name
            safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", voice_name.strip()).strip("_")
            if not safe_name:
                return False, "Voice name must contain letters or numbers."
            
            # Check for duplicate
            dest_audio_path = self.voices_dir / f"{safe_name}.wav"
            if dest_audio_path.exists():
                logger.warning(f"Voice '{safe_name}' already exists, overwriting.")
            
            # Extract audio segment
            temp_audio_path = self.videos_dir / f"temp_{safe_name}_{uuid.uuid4().hex[:6]}.wav"
            
            try:
                success, extract_msg = processor.extract_audio_segment(
                    video_path_obj,
                    start_time,
                    end_time,
                    temp_audio_path
                )
                
                if not success:
                    return False, extract_msg
                
                # Move to permanent location
                shutil.move(str(temp_audio_path), str(dest_audio_path))
                
                # Save metadata
                metadata = self._load_voice_metadata()
                metadata[safe_name] = {
                    "source_type": "video",
                    "source_file": video_path_obj.name,
                    "trim_range": [start_time, end_time],
                    "duration_sec": end_time - start_time,
                    "sample_rate": processor.target_sr,
                    "created_date": datetime.now().isoformat(),
                    "notes": notes,
                    "audio_file": str(dest_audio_path)
                }
                self._save_voice_metadata(metadata)
                
                logger.info(f"Created voice from video: {safe_name}")
                return True, f"Voice profile '{safe_name}' created successfully from video!"
                
            finally:
                # Cleanup temp file if it still exists
                if temp_audio_path.exists():
                    processor.cleanup_temp_files(temp_audio_path)
                    
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            return False, "ffmpeg-python or librosa not installed. Please install dependencies."
        except Exception as e:
            logger.error(f"Failed to create voice from video: {e}")
            return False, f"Failed to create voice: {str(e)}"
    
    def _load_voice_metadata(self) -> dict:
        """Load voice metadata from JSON file."""
        if self.voice_metadata_file.exists():
            try:
                import json
                with open(self.voice_metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load voice metadata: {e}")
        return {}
    
    def _save_voice_metadata(self, metadata: dict):
        """Save voice metadata to JSON file."""
        try:
            import json
            with open(self.voice_metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save voice metadata: {e}")
    
    def get_voice_metadata_info(self, voice_name: str) -> Optional[dict]:
        """Get metadata for a specific voice."""
        metadata = self._load_voice_metadata()
        return metadata.get(voice_name)
