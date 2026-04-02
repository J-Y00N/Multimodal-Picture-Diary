from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class AppSettings:
    base_model_id: str = os.getenv("BASE_MODEL_ID", "runwayml/stable-diffusion-v1-5")
    monet_repo_id: str = os.getenv("MONET_LORA_REPO_ID", "J-YOON/lora-monet-sd1.5")
    monet_weight_name: str = os.getenv("MONET_WEIGHT_NAME", "pytorch_lora_weights.safetensors")
    animate_repo_id: str = os.getenv("ANIMATE_LORA_REPO_ID", "J-YOON/animate-lora-sd1.5")
    animate_weight_name: str = os.getenv("ANIMATE_WEIGHT_NAME", "animate_v1-000005.safetensors")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_enabled: bool = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
    prompt_planner_mode: str = os.getenv("PROMPT_PLANNER_MODE", "template").lower()
    hf_token: str | None = os.getenv("HF_TOKEN")
    torch_device: str = os.getenv("TORCH_DEVICE", "auto")
    default_style: str = os.getenv("DEFAULT_STYLE", "monet")
    default_width: int = int(os.getenv("DEFAULT_WIDTH", "512"))
    default_height: int = int(os.getenv("DEFAULT_HEIGHT", "512"))
    default_steps: int = int(os.getenv("DEFAULT_STEPS", "28"))
    default_guidance_scale: float = float(os.getenv("DEFAULT_GUIDANCE_SCALE", "7.0"))
    max_prompt_chars: int = int(os.getenv("MAX_PROMPT_CHARS", "80"))


SETTINGS = AppSettings()
