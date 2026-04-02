from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from picture_diary.compose.export import image_to_png_bytes
from picture_diary.compose.page_template import compose_diary_page
from picture_diary.config import SETTINGS
from picture_diary.diffusion.generate import generate_diary_image
from picture_diary.diffusion.reference_modes import REFERENCE_STYLIZATION_MODES
from picture_diary.diffusion.style_registry import STYLE_REGISTRY, get_quality_preset
from picture_diary.llm.diary_rewriter import DiaryRewriter
from picture_diary.llm.prompt_builder import PromptBuilder
from picture_diary.llm.prompt_planner import PromptPlanner
from picture_diary.schemas import DiaryRequest


st.set_page_config(
    page_title="Multimodal Picture Diary",
    page_icon="🖼️",
    layout="wide",
)


def main() -> None:
    st.title("Multimodal Picture Diary")
    st.caption("Text-first diary generation with optional reference image support.")
    ai_rewrite_available = SETTINGS.openai_enabled and bool(SETTINGS.openai_api_key)
    planner_mode = SETTINGS.prompt_planner_mode
    effective_planner_label = {
        "rule_based": "Rule-based",
        "template": "Template",
        "openai": "OpenAI",
        "auto": "Auto",
    }.get(planner_mode, planner_mode)

    style_options = list(STYLE_REGISTRY)
    default_style_index = style_options.index(SETTINGS.default_style) if SETTINGS.default_style in style_options else 0

    with st.sidebar:
        generation_profile = st.radio(
            "Model usage",
            options=["lora_styled", "base_model_only"],
            format_func=lambda key: "LoRA styled" if key == "lora_styled" else "Base model only",
            index=0,
            help="Base model only disables the selected LoRA adapter so the foundation model can generalize more freely.",
        )
        use_base_model_only = generation_profile == "base_model_only"
        style_key = st.selectbox(
            "Style",
            options=style_options,
            format_func=lambda key: STYLE_REGISTRY[key].label,
            index=default_style_index,
        )
        spec = STYLE_REGISTRY[style_key]
        preset_options = [preset.key for preset in spec.presets]
        preset_key = st.selectbox(
            "Quality Preset",
            options=preset_options,
            format_func=lambda key: next(p.label for p in spec.presets if p.key == key),
            index=preset_options.index(spec.default_preset_key),
        )
        preset = get_quality_preset(style_key, preset_key)
        use_ai_rewrite = st.toggle("Use AI rewrite", value=False, disabled=not ai_rewrite_available)
        advanced_controls = st.toggle("Advanced controls", value=False)
        if advanced_controls:
            width = st.selectbox("Width", options=[512, 768], index=[512, 768].index(preset.width) if preset.width in [512, 768] else 0)
            height = st.selectbox("Height", options=[512, 768], index=[512, 768].index(preset.height) if preset.height in [512, 768] else 0)
            steps = st.slider("Steps", min_value=10, max_value=50, value=preset.steps, step=1)
            guidance_scale = st.slider("Guidance Scale", min_value=1.0, max_value=12.0, value=preset.guidance_scale, step=0.5)
            lora_scale = st.slider(
                "LoRA Strength",
                min_value=0.0,
                max_value=1.5,
                value=0.0 if use_base_model_only else preset.lora_scale,
                step=0.05,
                disabled=use_base_model_only,
            )
        else:
            width = preset.width
            height = preset.height
            steps = preset.steps
            guidance_scale = preset.guidance_scale
            lora_scale = 0.0 if use_base_model_only else preset.lora_scale

        seed_enabled = st.toggle("Use fixed seed", value=False)
        seed = st.number_input("Seed", min_value=0, max_value=2_147_483_647, value=42, step=1, disabled=not seed_enabled)

        st.caption(f"Preset: {width}x{height}, {steps} steps, CFG {guidance_scale:.1f}, LoRA {lora_scale:.2f}")
        if ai_rewrite_available:
            st.caption(f"AI rewrite available. Prompt planning mode: {effective_planner_label}.")
        else:
            st.caption(f"AI rewrite off. Prompt planning mode: {effective_planner_label}.")
        if use_base_model_only:
            st.caption("Base model only mode removes the selected LoRA adapter and style trigger for broader generalization.")

    diary_text = st.text_area(
        "Diary text",
        height=180,
        placeholder="오늘 있었던 일을 자유롭게 적어 주세요.",
    )
    negative_prompt = st.text_input(
        "Negative prompt",
        value=", ".join(
            part
            for part in [spec.negative_prompt, preset.negative_prompt_suffix]
            if part
        ),
    )
    reference_file = st.file_uploader(
        "Reference image (optional)",
        type=["png", "jpg", "jpeg"],
    )
    use_reference_mode = reference_file is not None
    reference_style_mode = "painterly"
    if use_reference_mode:
        reference_style_mode = st.selectbox(
            "Reference Style",
            options=list(REFERENCE_STYLIZATION_MODES),
            format_func=lambda key: REFERENCE_STYLIZATION_MODES[key]["label"],
            index=1,
        )
        st.caption(REFERENCE_STYLIZATION_MODES[reference_style_mode]["description"])

    mode_config = REFERENCE_STYLIZATION_MODES[reference_style_mode]
    effective_denoise_strength = mode_config["denoise_strength"]
    effective_lora_scale = min(1.5, round(lora_scale * mode_config["lora_scale_factor"], 2))
    effective_guidance_scale = max(1.0, min(12.0, round(guidance_scale + mode_config["guidance_delta"], 2)))

    if use_reference_mode and advanced_controls:
        effective_denoise_strength = st.slider(
            "Denoise Strength",
            min_value=0.15,
            max_value=0.8,
            value=float(effective_denoise_strength),
            step=0.05,
            help="Lower values preserve more photo structure. Higher values push further toward the learned style.",
        )
        effective_lora_scale = st.slider(
            "Reference LoRA Strength",
            min_value=0.0,
            max_value=1.5,
            value=float(effective_lora_scale),
            step=0.05,
            disabled=use_base_model_only,
        )
        effective_guidance_scale = st.slider(
            "Reference Guidance Scale",
            min_value=1.0,
            max_value=12.0,
            value=float(effective_guidance_scale),
            step=0.5,
        )

    col1, col2 = st.columns(2)
    with col1:
        generate_clicked = st.button("Generate diary page", use_container_width=True)
    with col2:
        if use_reference_mode:
            st.info(
                f"Reference mode: {REFERENCE_STYLIZATION_MODES[reference_style_mode]['label']} "
                f"(denoise {effective_denoise_strength:.2f}, LoRA {0.0 if use_base_model_only else effective_lora_scale:.2f})"
            )
        else:
            st.info("V1 권장 범위: text → prompt → image generation → diary page composition")

    if generate_clicked:
        if not diary_text.strip():
            st.warning("Diary text를 먼저 입력해 주세요.")
            return

        reference_image = Image.open(reference_file).convert("RGB") if reference_file else None
        rewriter = DiaryRewriter()
        builder = PromptBuilder(planner=PromptPlanner(mode=SETTINGS.prompt_planner_mode))
        try:
            rewritten = rewriter.rewrite(diary_text) if use_ai_rewrite else diary_text.strip()
            request = DiaryRequest(
                raw_diary=diary_text.strip(),
                rewritten_diary=rewritten,
                style_key=style_key,
                preset_key=preset_key,
                negative_prompt=negative_prompt.strip(),
                steps=steps,
                guidance_scale=effective_guidance_scale if use_reference_mode else guidance_scale,
                width=width,
                height=height,
                lora_scale=0.0 if use_base_model_only else (effective_lora_scale if use_reference_mode else lora_scale),
                use_base_model_only=use_base_model_only,
                denoise_strength=effective_denoise_strength,
                seed=int(seed) if seed_enabled else None,
                reference_image=reference_image,
            )

            with st.spinner("Generating image..."):
                result = generate_diary_image(request, builder)
                page = compose_diary_page(
                    diary_text=result.rewritten_diary,
                    generated_image=result.image,
                    prompt=result.prompt,
                    show_prompt_notes=False,
                )
        except Exception as exc:
            st.error(str(exc))
            return

        st.session_state["last_result"] = result
        st.session_state["last_page"] = page

    result = st.session_state.get("last_result")
    page = st.session_state.get("last_page")

    if result is not None and page is not None:
        st.subheader("Generated image")
        st.image(result.image)

        st.subheader("Composed diary page")
        st.image(page)

        with st.expander("Prompt details", expanded=False):
            st.write("Style / Preset")
            mode_label = "base-model-only" if result.use_base_model_only else "lora-styled"
            st.code(f"{result.style_key} / {result.preset_key} ({mode_label}, LoRA {result.lora_scale:.2f})")
            st.write("Generation Mode")
            st.code("img2img" if result.used_reference_image else "txt2img")
            st.write("Rewritten diary")
            st.code(result.rewritten_diary)
            st.write("Prompt")
            st.code(result.prompt)

        st.download_button(
            label="Download PNG",
            data=image_to_png_bytes(page),
            file_name="picture_diary_page.png",
            mime="image/png",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
