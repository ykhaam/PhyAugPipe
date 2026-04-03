from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass
class MetadataRecord:
    sample_id: str
    split: str
    source_metadata_ref: str
    original_caption: str
    shortlist_tags: list[str] = field(default_factory=list)
    shortlist_pass: bool = False
    local_video_path: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParseRecord:
    sample_id: str
    raw_parse: dict[str, Any]
    vision_checked_parse: dict[str, Any] | None = None
    physics_reasoning: str = ""
    score_components: dict[str, float] = field(default_factory=dict)
    penalties: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PromptRecord:
    sample_id: str
    original_caption: str
    cleaned_prompt: str = ""
    extended_prompt: str = ""
    revision_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
