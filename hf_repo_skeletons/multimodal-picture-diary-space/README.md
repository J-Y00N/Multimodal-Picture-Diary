---
title: Multimodal Picture Diary
emoji: "🖼️"
colorFrom: indigo
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# Multimodal Picture Diary Space

A Streamlit-based demo for diary-to-image generation using SD1.5 LoRA adapters.

## Runtime notes

- This Space is intended for inference only.
- The app uses LoRA adapters hosted on Hugging Face model repos.
- The Docker image should run Streamlit with XSRF protection disabled for HF Spaces compatibility.

## Suggested variables

- `MONET_LORA_REPO_ID=J-YOON/lora-monet-sd1.5`
- `ANIMATE_LORA_REPO_ID=J-YOON/animate-lora-sd1.5`
- `BASE_MODEL_ID=runwayml/stable-diffusion-v1-5`

## Suggested secrets

- `OPENAI_API_KEY` (optional)
- `HF_TOKEN` (optional)
