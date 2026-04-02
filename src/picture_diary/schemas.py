from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image


@dataclass
class DiaryRequest:
    raw_diary: str
    rewritten_diary: str
    style_key: str
    preset_key: str
    negative_prompt: str
    steps: int
    guidance_scale: float
    width: int
    height: int
    lora_scale: float = 1.0
    use_base_model_only: bool = False
    denoise_strength: float = 0.35
    seed: Optional[int] = None
    reference_image: Optional[Image.Image] = None


@dataclass
class GenerationResult:
    image: Image.Image
    prompt: str
    rewritten_diary: str
    style_key: str
    preset_key: str
    lora_scale: float
    use_base_model_only: bool = False
    used_reference_image: bool = False
