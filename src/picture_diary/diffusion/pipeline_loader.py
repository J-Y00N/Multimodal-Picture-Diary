from __future__ import annotations

from functools import lru_cache

import torch
from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionPipeline

from picture_diary.config import SETTINGS
from picture_diary.diffusion.style_registry import StyleSpec


def _resolve_device() -> str:
    if SETTINGS.torch_device != "auto":
        return SETTINGS.torch_device

    if torch.cuda.is_available():
        return "cuda"

    mps_backend = getattr(torch.backends, "mps", None)
    if mps_backend and torch.backends.mps.is_available():
        return "mps"

    return "cpu"


def _resolve_dtype(device: str) -> torch.dtype:
    if device == "cuda":
        return torch.float16
    if device == "mps":
        return torch.float32
    return torch.float32


def _load_base_pipeline(spec: StyleSpec, pipeline_cls):
    device = _resolve_device()
    dtype = _resolve_dtype(device)
    pipe = pipeline_cls.from_pretrained(
        spec.base_model,
        torch_dtype=dtype,
        safety_checker=None,
        token=SETTINGS.hf_token,
        use_safetensors=True,
    )
    pipe.load_lora_weights(
        spec.repo_id,
        weight_name=spec.weight_name,
        adapter_name=spec.key,
        token=SETTINGS.hf_token,
    )
    pipe = pipe.to(device)
    pipe.set_progress_bar_config(disable=True)
    if device in {"cpu", "mps"}:
        pipe.enable_attention_slicing()
    return pipe


@lru_cache(maxsize=2)
def load_text2img_pipeline(spec: StyleSpec) -> StableDiffusionPipeline:
    try:
        pipe = _load_base_pipeline(spec, StableDiffusionPipeline)
    except Exception as exc:
        message = str(exc)
        if "PEFT backend is required" in message:
            raise RuntimeError(
                "LoRA loading requires the 'peft' package. Install project dependencies again to include it."
            ) from exc
        raise RuntimeError(
            "Failed to load the Stable Diffusion pipeline. "
            "Check the base model id, Hugging Face repo ids, network access, and HF_TOKEN."
        ) from exc
    return pipe


@lru_cache(maxsize=2)
def load_img2img_pipeline(spec: StyleSpec) -> StableDiffusionImg2ImgPipeline:
    try:
        pipe = _load_base_pipeline(spec, StableDiffusionImg2ImgPipeline)
    except Exception as exc:
        message = str(exc)
        if "PEFT backend is required" in message:
            raise RuntimeError(
                "LoRA loading requires the 'peft' package. Install project dependencies again to include it."
            ) from exc
        raise RuntimeError(
            "Failed to load the Stable Diffusion img2img pipeline. "
            "Check the base model id, Hugging Face repo ids, network access, and HF_TOKEN."
        ) from exc
    return pipe
