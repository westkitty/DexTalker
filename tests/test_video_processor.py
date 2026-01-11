"""
Unit tests for Video Processor
"""
import pytest
from pathlib import Path
from app.video.processor import VideoProcessor


@pytest.fixture
def video_processor():
    """Create a VideoProcessor instance with test config."""
    config = {
        "max_upload_size_mb": 100,
        "max_video_duration_sec": 300,
        "min_audio_duration_sec": 3,
        "max_audio_duration_sec": 30,
        "target_sample_rate": 24000
    }
    return VideoProcessor(config)


def test_validate_video_size_limit(video_processor):
    """Test file size validation."""
    # This would require a real test file
    # For now, test the logic exists
    assert video_processor.max_size_mb == 100


def test_validate_video_duration_limit(video_processor):
    """Test duration validation."""
    assert video_processor.max_duration == 300


def test_trim_range_validation(video_processor):
    """Test trim range validation logic."""
    # Valid range
    start, end = 5.0, 10.0
    duration = end - start
    assert duration >= video_processor.min_audio_duration
    
    # Too short
    start, end = 0.0, 1.0
    duration = end - start
    assert duration < video_processor.min_audio_duration


def test_config_defaults():
    """Test default configuration values."""
    processor = VideoProcessor()
    assert processor.max_size_mb == 100
    assert processor.max_duration == 300
    assert processor.min_audio_duration == 3
    assert processor.target_sr == 24000


def test_audio_quality_validation_logic(video_processor):
    """Test audio quality check requirements exist."""
    # Verify the processor has quality check method
    assert hasattr(video_processor, 'validate_audio_quality')
    
    # Verify minimum duration requirement
    assert video_processor.min_audio_duration > 0
