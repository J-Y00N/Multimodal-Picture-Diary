# Multimodal Picture Diary

A personal refactor and rebuild of a diary-to-image application based on the original MS AI School team project.

## Overview

This repository focuses on three layers:

1. **Application layer**: a deployable Streamlit app that turns diary text into a stylized diary page.
2. **Generation layer**: Stable Diffusion 1.5 + LoRA adapters hosted on Hugging Face.
3. **Training provenance layer**: preserved config files, logs, and reconstruction notes for the original LoRA training runs.

This repository does **not** vendor the full `kohya_ss` training codebase. Instead, it documents the preserved training conditions as faithfully as possible.

## Run locally

```bash
cd /path/to/Multimodal-Picture-Diary
source .venv/bin/activate
cp .env.example .env
streamlit run app/main.py
```

## User-facing behavior

- No token entry is exposed in the app UI.
- End users only provide diary text and, optionally, a reference image.
- Text-only input uses `txt2img`.
- Reference image input uses `img2img`.

## Demo samples

Prompt used for the curated demo set:

```text
비온 뒤 집으로 가는 중!
```

Reference input image:

![Demo input](assets/demo/input/sample.jpg)

`text2img`

![Text2img Monet](assets/demo/output/demo_text2img_monet.png)
![Text2img Animate Landscape](assets/demo/output/demo_text2img_animate_landscape.png)

`img2img`

The `img2img` examples below use structure-preserving reference guidance tuned per style.
Monet uses `denoise_strength=0.25`, while Animate Landscape uses a slightly stronger stylization setting (`denoise_strength=0.32`, `lora_scale=0.95`) so the anime-style background is more visible.

![Img2img Monet](assets/demo/output/demo_img2img_monet.png)
![Img2img Animate Landscape](assets/demo/output/demo_img2img_animate_landscape.png)

Final diary-page export sample from the Streamlit flow:

![Diary page export](assets/demo/output/demo_diary_page_animate_landscape.png)

Generation settings for these demo assets are recorded under `assets/demo/metadata/`.

## Deployer setup

Secrets and model/provider settings are managed by the deployer through `.env` or server environment variables.
This repository is intentionally organized so that Hugging Face and OpenAI tokens stay outside the user-facing interface.

Core deployer settings:

- `HF_TOKEN`: optional but recommended for reliable Hugging Face model access.
- `OPENAI_API_KEY`: needed only if you want AI rewrite or OpenAI-based prompt planning.
- `OPENAI_ENABLED`: enables OpenAI-backed features when set to `true`.
- `PROMPT_PLANNER_MODE`: controls how prompts are designed before diffusion.

### Prompt planning modes

The app supports two prompt-design paths plus an automatic mode:

- `PROMPT_PLANNER_MODE=rule_based`
  Uses built-in keyword rules only. No OpenAI API call is made.
- `PROMPT_PLANNER_MODE=template`
  Uses prebuilt prompt templates such as `library_study`, `urban_walk`, `cafe_reflection`, and `travel_landscape`.
  This is useful when you want reusable prompt plans without writing them yourself.
- `PROMPT_PLANNER_MODE=openai`
  Uses the OpenAI API to dynamically plan `scene / subjects / mood / composition / extra_details`.
- `PROMPT_PLANNER_MODE=auto`
  In this mode, the app behaves like:
  - `OPENAI_ENABLED=true` -> use OpenAI dynamic planning
  - `OPENAI_ENABLED=false` -> use rule-based planning

Recommended deployer configurations:

```env
OPENAI_ENABLED=false
PROMPT_PLANNER_MODE=template
```

```env
OPENAI_ENABLED=true
PROMPT_PLANNER_MODE=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

Notes:

- `Use AI rewrite` is separate from prompt planning.
- If you want zero OpenAI API usage, set `OPENAI_ENABLED=false` and use `rule_based` or `template`.
- If you want dynamic prompts but not hardcoded rules, use `PROMPT_PLANNER_MODE=openai`.
- `template` mode is the easiest non-API option if you want reusable prompt plans without writing them from scratch.

## Suggested deployment split

- **GitHub repo**: this repository (`multimodal-picture-diary`)
- **HF model repos**: `J-YOON/lora-monet-sd1.5`, `J-YOON/animate-lora-sd1.5`
- **HF Space repo**: `multimodal-picture-diary-space` (template included under `hf_repo_skeletons/`)

## Development notes

1. Open this root folder.
2. Create and activate a virtual environment.
3. Fill in `.env` from `.env.example`.
4. Decide whether V1 will be text-only or text + reference image.
5. Implement `src/picture_diary/diffusion/generate.py` first.
6. Connect `app/main.py` only after the generator returns a PIL image reliably.

## Training provenance

See:

- `training/README.md`
- `training/configs/`
- `training/logs/`
- `docs/reproducibility_note.md`

## Hugging Face repo cleanup

See:

- `docs/hf_model_repo_cleanup.md`
- `hf_repo_skeletons/lora-monet-sd1.5/`
- `hf_repo_skeletons/animate-lora-sd1.5/`
- `hf_repo_skeletons/multimodal-picture-diary-space/`
