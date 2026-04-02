from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from picture_diary.compose.page_template import compose_diary_page
from picture_diary.config import SETTINGS
from picture_diary.diffusion.generate import generate_diary_image
from picture_diary.diffusion.reference_modes import REFERENCE_STYLIZATION_MODES
from picture_diary.diffusion.style_registry import get_quality_preset, get_style_spec
from picture_diary.llm.prompt_builder import PromptBuilder
from picture_diary.llm.prompt_planner import PromptPlanner
from picture_diary.schemas import DiaryRequest


PROMPT_TEXT = "비온 뒤 집으로 가는 중!"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate canonical demo assets for the README.")
    parser.add_argument("--img2img-denoise", type=float, default=0.2)
    return parser.parse_args()


def build_request(
    style_key: str,
    use_reference: bool,
    reference_image: Image.Image | None,
    *,
    img2img_denoise: float,
) -> DiaryRequest:
    spec = get_style_spec(style_key)
    preset = get_quality_preset(style_key, spec.default_preset_key)
    guidance_scale = preset.guidance_scale
    lora_scale = preset.lora_scale
    denoise_strength = 0.35
    preset_key = preset.key

    if use_reference:
        preserve_mode = REFERENCE_STYLIZATION_MODES["preserve_photo"]
        guidance_scale = max(1.0, min(12.0, preset.guidance_scale + preserve_mode["guidance_delta"]))
        lora_scale = min(1.3, round(preset.lora_scale * preserve_mode["lora_scale_factor"], 2))
        denoise_strength = img2img_denoise
        preset_key = f"{preset.key}_preserve_photo"

    return DiaryRequest(
        raw_diary=PROMPT_TEXT,
        rewritten_diary=PROMPT_TEXT,
        style_key=style_key,
        preset_key=preset_key,
        negative_prompt=", ".join(part for part in [spec.negative_prompt, preset.negative_prompt_suffix] if part),
        steps=preset.steps,
        guidance_scale=guidance_scale,
        width=preset.width,
        height=preset.height,
        lora_scale=lora_scale,
        denoise_strength=denoise_strength,
        seed=42,
        reference_image=reference_image if use_reference else None,
    )


def write_metadata(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = ROOT / "assets" / "demo" / "output"
    metadata_dir = ROOT / "assets" / "demo" / "metadata"
    reference_image = Image.open(ROOT / "assets" / "demo" / "input" / "sample.jpg").convert("RGB")

    planner = PromptPlanner(mode=SETTINGS.prompt_planner_mode)
    builder = PromptBuilder(planner=planner)

    jobs = [
        ("monet", False, "demo_text2img_monet.png", "demo_text2img_monet.json"),
        ("animate_landscape", False, "demo_text2img_animate_landscape.png", "demo_text2img_animate_landscape.json"),
        ("monet", True, "demo_img2img_monet.png", "demo_img2img_monet.json"),
        (
            "animate_landscape",
            True,
            "demo_img2img_animate_landscape.png",
            "demo_img2img_animate_landscape.json",
        ),
    ]

    final_page_image: Image.Image | None = None
    final_page_prompt = ""

    for style_key, use_reference, image_name, metadata_name in jobs:
        request = build_request(
            style_key,
            use_reference,
            reference_image,
            img2img_denoise=args.img2img_denoise,
        )
        result = generate_diary_image(request, builder)

        image_path = output_dir / image_name
        image_path.parent.mkdir(parents=True, exist_ok=True)
        result.image.save(image_path)

        metadata = {
            "mode": "img2img" if use_reference else "text2img",
            "style": style_key,
            "preset": get_style_spec(style_key).default_preset_key,
            "seed": 42,
            "prompt_text": PROMPT_TEXT,
            "reference_image": "assets/demo/input/sample.jpg" if use_reference else None,
            "reference_mode": "preserve_photo" if use_reference else None,
            "denoise_strength": request.denoise_strength if use_reference else None,
            "lora_scale": request.lora_scale,
            "resolved_prompt": result.prompt,
        }
        write_metadata(metadata_dir / metadata_name, metadata)
        print(f"saved {image_path}")

        if style_key == "animate_landscape" and use_reference:
            final_page_image = result.image.copy()
            final_page_prompt = result.prompt

    if final_page_image is None:
        raise RuntimeError("Missing animate_landscape img2img result for diary page export.")

    page = compose_diary_page(
        diary_text=PROMPT_TEXT,
        generated_image=final_page_image,
        prompt=final_page_prompt,
        show_prompt_notes=False,
    )
    page_path = output_dir / "demo_diary_page_animate_landscape.png"
    page.save(page_path)
    write_metadata(
        metadata_dir / "demo_diary_page_animate_landscape.json",
        {
            "mode": "diary_page_export",
            "source_image": "assets/demo/output/demo_img2img_animate_landscape.png",
            "style": "animate_landscape",
            "prompt_text": PROMPT_TEXT,
            "diary_text": PROMPT_TEXT,
            "show_prompt_notes": False,
        },
    )
    print(f"saved {page_path}")


if __name__ == "__main__":
    main()
