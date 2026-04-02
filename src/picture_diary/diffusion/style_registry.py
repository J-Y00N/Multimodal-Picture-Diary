from __future__ import annotations

from dataclasses import dataclass

from picture_diary.config import SETTINGS


@dataclass(frozen=True)
class QualityPreset:
    key: str
    label: str
    width: int
    height: int
    steps: int
    guidance_scale: float
    lora_scale: float
    negative_prompt_suffix: str = ""


@dataclass(frozen=True)
class StyleSpec:
    key: str
    label: str
    base_model: str
    repo_id: str
    weight_name: str
    trigger: str
    style_note: str
    negative_prompt: str
    default_preset_key: str
    presets: tuple[QualityPreset, ...]


STYLE_REGISTRY = {
    "monet": StyleSpec(
        key="monet",
        label="Monet",
        base_model=SETTINGS.base_model_id,
        repo_id=SETTINGS.monet_repo_id,
        weight_name=SETTINGS.monet_weight_name,
        trigger="msl monet",
        style_note="soft brush strokes, impressionist color palette",
        negative_prompt="low quality, blurry, distorted anatomy, watermark, text",
        default_preset_key="balanced",
        presets=(
            QualityPreset(
                key="fast_preview",
                label="Fast Preview",
                width=512,
                height=512,
                steps=18,
                guidance_scale=6.5,
                lora_scale=0.85,
            ),
            QualityPreset(
                key="balanced",
                label="Balanced",
                width=768,
                height=768,
                steps=28,
                guidance_scale=7.5,
                lora_scale=0.95,
            ),
            QualityPreset(
                key="detail_focus",
                label="Detail Focus",
                width=768,
                height=768,
                steps=32,
                guidance_scale=7.0,
                lora_scale=0.9,
                negative_prompt_suffix="oversaturated, muddy colors, chaotic brush strokes",
            ),
        ),
    ),
    "animate_landscape": StyleSpec(
        key="animate_landscape",
        label="Animate Landscape",
        base_model=SETTINGS.base_model_id,
        repo_id=SETTINGS.animate_repo_id,
        weight_name=SETTINGS.animate_weight_name,
        trigger="sms landscape",
        style_note="cinematic anime-style landscape, sky-rich composition",
        negative_prompt="low quality, deformed, extra limbs, watermark, text",
        default_preset_key="balanced",
        presets=(
            QualityPreset(
                key="fast_preview",
                label="Fast Preview",
                width=512,
                height=512,
                steps=18,
                guidance_scale=6.0,
                lora_scale=0.85,
            ),
            QualityPreset(
                key="balanced",
                label="Balanced",
                width=768,
                height=768,
                steps=26,
                guidance_scale=7.0,
                lora_scale=0.95,
            ),
            QualityPreset(
                key="sky_drama",
                label="Sky Drama",
                width=768,
                height=768,
                steps=34,
                guidance_scale=8.0,
                lora_scale=1.0,
                negative_prompt_suffix="flat lighting, dull sky",
            ),
        ),
    ),
}


def get_style_spec(style_key: str) -> StyleSpec:
    try:
        return STYLE_REGISTRY[style_key]
    except KeyError as exc:
        available = ", ".join(sorted(STYLE_REGISTRY))
        raise ValueError(f"Unknown style '{style_key}'. Available styles: {available}") from exc


def get_quality_preset(style_key: str, preset_key: str) -> QualityPreset:
    spec = get_style_spec(style_key)
    for preset in spec.presets:
        if preset.key == preset_key:
            return preset
    available = ", ".join(preset.key for preset in spec.presets)
    raise ValueError(f"Unknown preset '{preset_key}' for style '{style_key}'. Available presets: {available}")
