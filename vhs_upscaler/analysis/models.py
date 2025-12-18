"""
Data models for video analysis system.

This module defines shared enums and dataclasses used by all analyzer backends
(Python+OpenCV, Bash, FFprobe-only) to ensure consistent analysis output.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class ScanType(Enum):
    """Video scan type (progressive vs interlaced)."""
    PROGRESSIVE = "progressive"
    INTERLACED_TFF = "interlaced_tff"  # Top Field First
    INTERLACED_BFF = "interlaced_bff"  # Bottom Field First
    TELECINE = "telecine"
    UNKNOWN = "unknown"


class ContentType(Enum):
    """Type of video content."""
    LIVE_ACTION = "live_action"
    ANIMATION = "animation"
    MIXED = "mixed"
    TALKING_HEAD = "talking_head"
    SPORTS = "sports"
    UNKNOWN = "unknown"


class NoiseLevel(Enum):
    """Noise level in video."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SEVERE = "severe"


class SourceFormat(Enum):
    """Detected source format."""
    VHS = "vhs"
    SVHS = "svhs"
    DVD = "dvd"
    BROADCAST = "broadcast"
    DIGITAL = "digital"
    UNKNOWN = "unknown"


@dataclass
class VideoAnalysis:
    """
    Complete video analysis results from any backend.

    This dataclass is the common output format for all analyzer backends,
    ensuring consistent structure regardless of which backend performed the analysis.
    """

    # File info
    filepath: str
    filename: str
    filesize_mb: float
    duration_seconds: float

    # Technical properties (required fields)
    width: int
    height: int
    framerate: float
    framerate_fraction: str  # e.g., "30000/1001" for 29.97fps
    codec: str
    pixel_format: str

    # Detected characteristics (required fields)
    scan_type: ScanType
    content_type: ContentType
    source_format: SourceFormat
    noise_level: NoiseLevel
    estimated_quality_score: float  # 0-100 scale

    # Optional technical properties (some backends may not populate these)
    bitrate_kbps: Optional[int] = None

    # VHS-specific artifacts
    has_tracking_errors: bool = False
    has_color_bleeding: bool = False
    has_head_switching_noise: bool = False
    has_dropout_lines: bool = False
    has_jitter: bool = False

    # Audio properties
    audio_codec: Optional[str] = None
    audio_channels: int = 2
    audio_sample_rate: int = 44100
    audio_bitrate_kbps: int = 128

    # Recommendations
    recommended_tools: List[str] = field(default_factory=list)
    recommended_settings: Dict[str, Any] = field(default_factory=dict)
    processing_notes: List[str] = field(default_factory=list)
    estimated_processing_time: str = ""

    # Metadata
    analyzer_backend: str = ""  # Which backend produced this analysis
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert VideoAnalysis to dictionary for JSON serialization."""
        return {
            "filepath": self.filepath,
            "filename": self.filename,
            "filesize_mb": self.filesize_mb,
            "duration_seconds": self.duration_seconds,
            "width": self.width,
            "height": self.height,
            "framerate": self.framerate,
            "framerate_fraction": self.framerate_fraction,
            "codec": self.codec,
            "pixel_format": self.pixel_format,
            "bitrate_kbps": self.bitrate_kbps,
            "scan_type": self.scan_type.value,
            "content_type": self.content_type.value,
            "source_format": self.source_format.value,
            "noise_level": self.noise_level.value,
            "estimated_quality_score": self.estimated_quality_score,
            "has_tracking_errors": self.has_tracking_errors,
            "has_color_bleeding": self.has_color_bleeding,
            "has_head_switching_noise": self.has_head_switching_noise,
            "has_dropout_lines": self.has_dropout_lines,
            "has_jitter": self.has_jitter,
            "audio_codec": self.audio_codec,
            "audio_channels": self.audio_channels,
            "audio_sample_rate": self.audio_sample_rate,
            "audio_bitrate_kbps": self.audio_bitrate_kbps,
            "recommended_tools": self.recommended_tools,
            "recommended_settings": self.recommended_settings,
            "processing_notes": self.processing_notes,
            "estimated_processing_time": self.estimated_processing_time,
            "analyzer_backend": self.analyzer_backend,
            "analysis_timestamp": self.analysis_timestamp,
        }

    def to_json(self, filepath: str) -> None:
        """Export VideoAnalysis to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoAnalysis':
        """Create VideoAnalysis from dictionary (for loading JSON)."""
        # Convert enum strings back to enum values
        data['scan_type'] = ScanType(data['scan_type'])
        data['content_type'] = ContentType(data['content_type'])
        data['source_format'] = SourceFormat(data['source_format'])
        data['noise_level'] = NoiseLevel(data['noise_level'])

        return cls(**data)

    @classmethod
    def from_json(cls, filepath: str) -> 'VideoAnalysis':
        """Load VideoAnalysis from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_summary(self) -> str:
        """Generate a human-readable summary of the analysis."""
        lines = [
            "=== Video Analysis Report ===",
            "",
            f"File: {self.filename}",
            f"Duration: {self._format_duration()}",
            f"Resolution: {self.width}x{self.height} @ {self.framerate:.2f} fps",
            f"Codec: {self.codec} ({self.pixel_format})",
            f"Bitrate: {f'{self.bitrate_kbps} kbps' if self.bitrate_kbps is not None else 'Unknown'}",
            "",
            f"Scan Type: {self.scan_type.value.replace('_', ' ').title()}",
            f"Content Type: {self.content_type.value.replace('_', ' ').title()}",
            f"Source Format: {self.source_format.value.upper()}",
            f"Noise Level: {self.noise_level.value.upper()}",
            f"Quality Score: {self.estimated_quality_score:.1f}/100",
            "",
        ]

        # VHS artifacts section
        artifacts = []
        if self.has_head_switching_noise:
            artifacts.append("Head switching noise")
        if self.has_color_bleeding:
            artifacts.append("Color bleeding")
        if self.has_tracking_errors:
            artifacts.append("Tracking errors")
        if self.has_dropout_lines:
            artifacts.append("Dropout lines")
        if self.has_jitter:
            artifacts.append("Frame jitter")

        if artifacts:
            lines.append("Detected VHS Artifacts:")
            for artifact in artifacts:
                lines.append(f"  ✓ {artifact}")
            lines.append("")

        # Audio info
        if self.audio_codec:
            lines.append("Audio:")
            lines.append(f"  Codec: {self.audio_codec}")
            lines.append(f"  Channels: {self.audio_channels}")
            lines.append(f"  Sample Rate: {self.audio_sample_rate} Hz")
            lines.append(f"  Bitrate: {self.audio_bitrate_kbps} kbps")
            lines.append("")

        # Recommendations
        if self.recommended_settings:
            preset = self.recommended_settings.get('preset', 'unknown')
            lines.append(f"Recommended Preset: {preset}")
            lines.append("Recommended Settings:")
            for key, value in self.recommended_settings.items():
                if key != 'preset':
                    lines.append(f"  - {key}: {value}")
            lines.append("")

        # Processing notes
        if self.processing_notes:
            lines.append("Processing Notes:")
            for note in self.processing_notes:
                lines.append(f"  • {note}")
            lines.append("")

        # Timing
        if self.estimated_processing_time:
            lines.append(f"Estimated Processing Time: {self.estimated_processing_time}")
            lines.append("")

        lines.append(f"Analysis Backend: {self.analyzer_backend}")
        lines.append(f"Analysis Timestamp: {self.analysis_timestamp}")

        return "\n".join(lines)

    def _format_duration(self) -> str:
        """Format duration in HH:MM:SS."""
        hours = int(self.duration_seconds // 3600)
        minutes = int((self.duration_seconds % 3600) // 60)
        seconds = int(self.duration_seconds % 60)

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
