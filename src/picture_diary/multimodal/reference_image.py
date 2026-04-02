from __future__ import annotations

from typing import Optional

from PIL import Image, ImageOps


def extract_reference_hint(reference_image: Optional[Image.Image]) -> str:
    """V1 keeps this intentionally simple.

    Future options:
    - BLIP / caption model for automatic visual hints
    - IP-Adapter for image-guided generation
    - ControlNet for pose / edge / composition guidance
    """
    if reference_image is None:
        return ""
    reference_image = ImageOps.exif_transpose(reference_image)
    width, height = reference_image.size
    orientation = "portrait" if height > width else "landscape"
    return f"reference image provided, {orientation} composition"


def prepare_reference_image(reference_image: Image.Image, width: int, height: int) -> Image.Image:
    target_width = max(64, width - (width % 8))
    target_height = max(64, height - (height % 8))
    normalized = ImageOps.exif_transpose(reference_image).convert("RGB")
    return ImageOps.fit(
        normalized,
        (target_width, target_height),
        method=Image.Resampling.LANCZOS,
    )
