from __future__ import annotations


REFERENCE_STYLIZATION_MODES = {
    "preserve_photo": {
        "label": "Preserve Photo",
        "description": "Keep the original composition and structure, with only a light Monet feel.",
        "denoise_strength": 0.2,
        "lora_scale_factor": 0.8,
        "guidance_delta": -0.5,
    },
    "painterly": {
        "label": "Painterly",
        "description": "Balance the original photo with a visible painted texture.",
        "denoise_strength": 0.48,
        "lora_scale_factor": 1.08,
        "guidance_delta": 0.1,
    },
    "dreamy_abstract": {
        "label": "Dreamy Abstract",
        "description": "Push further into a stylized, painterly interpretation of the scene.",
        "denoise_strength": 0.58,
        "lora_scale_factor": 1.15,
        "guidance_delta": 0.3,
    },
}
