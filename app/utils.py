"""
Utility functions for DexTalker UI and text processing.
"""
import re
from pathlib import Path
from typing import Tuple


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_text_stats(text: str) -> Tuple[int, int, float]:
    """
    Get text statistics.
    
    Returns:
        Tuple[int, int, float]: (character count, word count, estimated duration in seconds)
    """
    chars = len(text)
    words = len(text.split())
    # Rough estimate: ~150 words per minute for TTS
    duration = (words / 150) * 60 if words > 0 else 0
    return chars, words, duration


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def preprocess_text(text: str, remove_urls: bool = False, remove_special: bool = False) -> str:
    """
    Preprocess text for better TTS output.
    
    Args:
        text: Input text
        remove_urls: Remove URLs from text
        remove_special: Remove special characters (keep alphanumeric and punctuation)
    
    Returns:
        Cleaned text
    """
    result = text
    
    if remove_urls:
        # Remove URLs
        result = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', result)
        result = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', result)
    
    if remove_special:
        # Keep letters, numbers, spaces, and basic punctuation
        result = re.sub(r'[^a-zA-Z0-9\s.,!?;:\'\"-]', '', result)
    
    # Normalize whitespace
    result = re.sub(r'\s+', ' ', result)
    result = result.strip()
    
    return result


def get_voice_metadata(voice_path: Path) -> dict:
    """
    Get metadata for a voice file.
    
    Returns:
        dict with keys: duration, size, date_added
    """
    if not voice_path.exists():
        return {"duration": "N/A", "size": "N/A", "date_added": "N/A"}
    
    size = voice_path.stat().st_size
    date_added = voice_path.stat().st_mtime
    
    # Try to get audio duration
    duration_str = "N/A"
    try:
        import soundfile as sf
        data, sr = sf.read(str(voice_path))
        duration = len(data) / sr
        duration_str = format_duration(duration)
    except Exception:
        pass
    
    from datetime import datetime
    date_str = datetime.fromtimestamp(date_added).strftime("%Y-%m-%d")
    
    return {
        "duration": duration_str,
        "size": format_file_size(size),
        "date_added": date_str
    }


# Text presets/templates
DEFAULT_PRESETS = {
    "Good Morning": "Good morning! I hope you have a wonderful day ahead.",
    "Announcement": "Attention everyone, I have an important announcement to make.",
    "Greeting": "Hello and welcome! It's great to have you here.",
    "Thank You": "Thank you so much for your time and attention. I really appreciate it.",
    "Goodbye": "Thank you for listening. Have a great day and take care!",
}


def get_text_presets() -> dict:
    """Get available text presets."""
    return DEFAULT_PRESETS.copy()
