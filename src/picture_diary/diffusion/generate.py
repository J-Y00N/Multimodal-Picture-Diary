from __future__ import annotations

import torch

from picture_diary.diffusion.pipeline_loader import load_img2img_pipeline, load_text2img_pipeline
from picture_diary.diffusion.style_registry import get_style_spec
from picture_diary.llm.prompt_builder import PromptBuilder
from picture_diary.multimodal.reference_image import prepare_reference_image
from picture_diary.schemas import DiaryRequest, GenerationResult


def generate_diary_image(request: DiaryRequest, prompt_builder: PromptBuilder) -> GenerationResult:
    spec = get_style_spec(request.style_key)
    prompt = prompt_builder.build(
        diary_text=request.rewritten_diary,
        style_key=request.style_key,
        reference_image=request.reference_image,
    )
    use_reference_image = request.reference_image is not None
    pipe = load_img2img_pipeline(spec) if use_reference_image else load_text2img_pipeline(spec)

    generator = None
    if request.seed is not None:
        generator = torch.Generator(device=pipe.device).manual_seed(request.seed)

    if hasattr(pipe, "set_adapters"):
        pipe.set_adapters([spec.key], adapter_weights=[request.lora_scale])

    try:
        if use_reference_image:
            prepared_image = prepare_reference_image(
                request.reference_image,
                width=request.width,
                height=request.height,
            )
            result = pipe(
                prompt=prompt,
                image=prepared_image,
                strength=request.denoise_strength,
                negative_prompt=request.negative_prompt or spec.negative_prompt,
                num_inference_steps=request.steps,
                guidance_scale=request.guidance_scale,
                generator=generator,
            )
        else:
            result = pipe(
                prompt=prompt,
                negative_prompt=request.negative_prompt or spec.negative_prompt,
                num_inference_steps=request.steps,
                guidance_scale=request.guidance_scale,
                width=request.width,
                height=request.height,
                generator=generator,
            )
    except RuntimeError as exc:
        raise RuntimeError(
            "Image generation failed. Try a smaller resolution, fewer steps, or a different device."
        ) from exc

    image = result.images[0]
    return GenerationResult(
        image=image,
        prompt=prompt,
        rewritten_diary=request.rewritten_diary,
        style_key=request.style_key,
        preset_key=request.preset_key,
        lora_scale=request.lora_scale,
        used_reference_image=use_reference_image,
    )
