from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from picture_diary.diffusion.generate import generate_diary_image
from picture_diary.diffusion.reference_modes import REFERENCE_STYLIZATION_MODES
from picture_diary.diffusion.style_registry import get_quality_preset, get_style_spec
from picture_diary.llm.prompt_builder import PromptBuilder
from picture_diary.schemas import DiaryRequest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate comparison samples for a style preset.")
    parser.add_argument("--style", default="monet")
    parser.add_argument("--preset", action="append", dest="presets")
    parser.add_argument("--text", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="outputs/quality_samples")
    parser.add_argument("--steps-scale", type=float, default=1.0)
    parser.add_argument("--reference-image")
    parser.add_argument("--reference-mode", action="append", dest="reference_modes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spec = get_style_spec(args.style)
    presets = args.presets or [preset.key for preset in spec.presets]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    builder = PromptBuilder()
    reference_image = Image.open(args.reference_image).convert("RGB") if args.reference_image else None
    reference_modes = args.reference_modes or ["painterly"]

    for preset_key in presets:
        preset = get_quality_preset(args.style, preset_key)

        if reference_image is None:
            request = DiaryRequest(
                raw_diary=args.text,
                rewritten_diary=args.text,
                style_key=args.style,
                preset_key=preset.key,
                negative_prompt=", ".join(
                    part for part in [spec.negative_prompt, preset.negative_prompt_suffix] if part
                ),
                steps=max(1, int(round(preset.steps * args.steps_scale))),
                guidance_scale=preset.guidance_scale,
                width=preset.width,
                height=preset.height,
                lora_scale=preset.lora_scale,
                seed=args.seed,
            )
            result = generate_diary_image(request, builder)

            stem = f"{args.style}_{preset.key}_seed{args.seed}"
            image_path = output_dir / f"{stem}.png"
            prompt_path = output_dir / f"{stem}.txt"

            result.image.save(image_path)
            prompt_path.write_text(result.prompt + "\n", encoding="utf-8")
            print(f"saved_image={image_path}")
            print(f"saved_prompt={prompt_path}")
            continue

        for reference_mode in reference_modes:
            mode = REFERENCE_STYLIZATION_MODES[reference_mode]
            request = DiaryRequest(
                raw_diary=args.text,
                rewritten_diary=args.text,
                style_key=args.style,
                preset_key=f"{preset.key}_{reference_mode}",
                negative_prompt=", ".join(
                    part for part in [spec.negative_prompt, preset.negative_prompt_suffix] if part
                ),
                steps=max(1, int(round(preset.steps * args.steps_scale))),
                guidance_scale=max(1.0, min(12.0, preset.guidance_scale + mode["guidance_delta"])),
                width=preset.width,
                height=preset.height,
                lora_scale=min(1.3, round(preset.lora_scale * mode["lora_scale_factor"], 2)),
                denoise_strength=mode["denoise_strength"],
                seed=args.seed,
                reference_image=reference_image,
            )
            result = generate_diary_image(request, builder)

            stem = f"{args.style}_{preset.key}_{reference_mode}_seed{args.seed}"
            image_path = output_dir / f"{stem}.png"
            prompt_path = output_dir / f"{stem}.txt"

            result.image.save(image_path)
            prompt_path.write_text(result.prompt + "\n", encoding="utf-8")
            print(f"saved_image={image_path}")
            print(f"saved_prompt={prompt_path}")


if __name__ == "__main__":
    main()
