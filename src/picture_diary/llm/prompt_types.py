from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PromptPlan:
    scene: str
    subjects: list[str] = field(default_factory=list)
    mood: str = "calm, intimate, diary-like"
    composition: str = ""
    extra_details: list[str] = field(default_factory=list)
