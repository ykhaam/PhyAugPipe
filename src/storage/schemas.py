from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MetadataRecord:
    sample_id: str
    split: str
    source_metadata_ref: str
    original_caption: str
    shortlist_tags: List[str] = field(default_factory=list)
    shortlist_pass: bool = False
    local_video_path: Optional[str] = None
    local_video_found: bool = False
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FrameRecord:
    sample_id: str
    frame_paths: List[str]
    sampling_strategy: str
    num_frames_requested: int
    num_frames_extracted: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseRecord:
    sample_id: str
    raw_parse: Dict[str, Any]
    vision_checked_parse: Dict[str, Any]
    physics_reasoning: str
    score_components: Dict[str, float]
    penalties: Dict[str, float]
    physics_richness: float
    physics_label: str


@dataclass
class PromptRecord:
    sample_id: str
    original_caption: str
    cleaned_prompt: str
    extended_prompt: str
    revision_notes: List[str] = field(default_factory=list)
