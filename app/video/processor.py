"""
Video processing module for DexTalker Video Voice Clone feature.
Handles video upload, validation, trimming, and audio extraction.
"""
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict
import json

logger = logging.getLogger("DexTalker.Video")

class VideoProcessor:
    """
    Processes videos for voice cloning: validation, trimming, and audio extraction.
    Uses ffmpeg for video/audio operations and librosa for audio analysis.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize video processor with configuration.
        
        Args:
            config: Configuration dict with limits and settings
        """
        config = config or {}
        self.max_size_mb = config.get("max_upload_size_mb", 100)
        self.max_duration = config.get("max_video_duration_sec", 300)
        self.min_audio_duration = config.get("min_audio_duration_sec", 3)
        self.max_audio_duration = config.get("max_audio_duration_sec", 30)
        self.target_sr = config.get("target_sample_rate", 24000)
        
        logger.info(f"VideoProcessor initialized: max_size={self.max_size_mb}MB, "
                   f"max_duration={self.max_duration}s, target_sr={self.target_sr}Hz")
    
    def validate_video(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate video file size and duration.
        
        Args:
            file_path: Path to video file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Check file exists
            if not file_path.exists():
                return False, "File not found"
            
            # Check file size
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_size_mb:
                return False, f"File size ({size_mb:.1f}MB) exceeds {self.max_size_mb}MB limit"
            
            # Check duration using ffprobe
            try:
                import ffmpeg
                probe = ffmpeg.probe(str(file_path))
                duration = float(probe['format']['duration'])
                
                if duration > self.max_duration:
                    return False, f"Video duration ({duration:.1f}s) exceeds {self.max_duration}s limit"
                    
                logger.info(f"Video validated: {file_path.name}, {size_mb:.1f}MB, {duration:.1f}s")
                return True, f"Valid ({size_mb:.1f}MB, {duration:.1f}s)"
                
            except Exception as e:
                logger.error(f"Failed to probe video: {e}")
                return False, f"Failed to read video metadata: {str(e)}"
                
        except Exception as e:
            logger.error(f"Video validation error: {e}")
            return False, f"Validation error: {str(e)}"
    
    def get_video_info(self, file_path: Path) -> Optional[Dict]:
        """
        Get video metadata (duration, codec, resolution, etc.).
        
        Args:
            file_path: Path to video file
            
        Returns:
            Dict with video info or None if failed
        """
        try:
            import ffmpeg
            probe = ffmpeg.probe(str(file_path))
            
            video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            
            info = {
                'duration': float(probe['format']['duration']),
                'size_mb': file_path.stat().st_size / (1024 * 1024),
                'format': probe['format']['format_name'],
                'has_video': len(video_streams) > 0,
                'has_audio': len(audio_streams) > 0,
            }
            
            if video_streams:
                v = video_streams[0]
                info.update({
                    'width': v.get('width'),
                    'height': v.get('height'),
                    'video_codec': v.get('codec_name'),
                })
            
            if audio_streams:
                a = audio_streams[0]
                info.update({
                    'audio_codec': a.get('codec_name'),
                    'audio_sample_rate': a.get('sample_rate'),
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return None
    
    def extract_audio_segment(
        self,
        video_path: Path,
        start_sec: float,
        end_sec: float,
        output_path: Path
    ) -> Tuple[bool, str]:
        """
        Extract audio from a video segment and save as WAV.
        
        Args:
            video_path: Source video file
            start_sec: Start time in seconds
            end_sec: End time in seconds
            output_path: Where to save extracted audio (WAV)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            import ffmpeg
            
            # Validate trim range
            duration = end_sec - start_sec
            if duration < self.min_audio_duration:
                return False, f"Segment too short ({duration:.1f}s). Minimum {self.min_audio_duration}s required"
            
            if duration > self.max_audio_duration:
                return False, f"Segment too long ({duration:.1f}s). Maximum {self.max_audio_duration}s allowed"
            
            logger.info(f"Extracting audio: {start_sec:.2f}s to {end_sec:.2f}s ({duration:.2f}s)")
            
            # Create parent directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Extract audio using ffmpeg
            # -ss: start time, -t: duration
            # -acodec pcm_s16le: 16-bit PCM WAV
            # -ar: sample rate, -ac 1: mono
            stream = ffmpeg.input(str(video_path), ss=start_sec, t=duration)
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec='pcm_s16le',
                ar=self.target_sr,
                ac=1,  # mono
                loglevel='error'
            )
            
            # Run extraction
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
            # Validate extracted audio
            if not output_path.exists() or output_path.stat().st_size == 0:
                return False, "Audio extraction produced empty file"
            
            valid, msg = self.validate_audio_quality(output_path)
            if not valid:
                # Clean up bad output
                if output_path.exists():
                    output_path.unlink()
                return False, msg
            
            logger.info(f"Audio extracted successfully: {output_path}")
            return True, f"Audio extracted: {duration:.1f}s at {self.target_sr}Hz"
            
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            # Clean up on error
            if output_path.exists():
                try:
                    output_path.unlink()
                except:
                    pass
            
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower():
                return False, "FFmpeg error. Ensure ffmpeg is installed and video format is supported."
            return False, f"Extraction failed: {error_msg}"
    
    def validate_audio_quality(self, audio_path: Path) -> Tuple[bool, str]:
        """
        Validate extracted audio quality (duration, silence check).
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            import librosa
            import numpy as np
            
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)
            duration = len(y) / sr
            
            logger.info(f"Audio analysis: duration={duration:.2f}s, sr={sr}Hz")
            
            # Check minimum duration
            if duration < self.min_audio_duration:
                return False, f"Audio too short ({duration:.1f}s). Minimum {self.min_audio_duration}s required"
            
            # Check for silence (RMS energy analysis)
            rms = librosa.feature.rms(y=y)[0]
            mean_rms = np.mean(rms)
            
            if mean_rms < 0.005:  # Very quiet threshold
                return False, "Audio appears to be silent or very quiet. Please select a segment with clear speech."
            
            # Check for clipping
            if np.max(np.abs(y)) > 0.99:
                logger.warning("Audio may be clipping (very loud)")
            
            logger.info(f"Audio quality OK: RMS={mean_rms:.4f}")
            return True, f"Audio quality good ({duration:.1f}s, RMS={mean_rms:.4f})"
            
        except Exception as e:
            logger.error(f"Audio quality check failed: {e}")
            return False, f"Failed to analyze audio: {str(e)}"
    
    def cleanup_temp_files(self, *file_paths: Path):
        """
        Clean up temporary files.
        
        Args:
            file_paths: Paths to files to delete
        """
        for path in file_paths:
            if path and path.exists():
                try:
                    path.unlink()
                    logger.info(f"Cleaned up: {path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {path}: {e}")
