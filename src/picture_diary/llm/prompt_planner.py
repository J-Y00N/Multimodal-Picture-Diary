from __future__ import annotations

import json
from dataclasses import dataclass

from picture_diary.config import SETTINGS
from picture_diary.llm.prompt_templates import PROMPT_TEMPLATES
from picture_diary.llm.prompt_types import PromptPlan
from picture_diary.multimodal.reference_image import extract_reference_hint

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency at runtime
    OpenAI = None

@dataclass
class PromptPlanner:
    mode: str = SETTINGS.prompt_planner_mode

    def _resolve_mode(self) -> str:
        mode = self.mode.lower()
        if mode in {"openai", "rule_based", "template"}:
            return mode
        return "openai" if SETTINGS.openai_enabled else "rule_based"

    def _template_plan(self, diary_text: str, reference_image=None, fallback_plan: PromptPlan | None = None) -> PromptPlan:
        text_lower = diary_text.lower()
        for template in PROMPT_TEMPLATES:
            if any(trigger.lower() in text_lower for trigger in template.triggers):
                plan = template.plan
                reference_hint = extract_reference_hint(reference_image)
                return PromptPlan(
                    scene=plan.scene,
                    subjects=list(plan.subjects),
                    mood=plan.mood,
                    composition=reference_hint or plan.composition,
                    extra_details=list(plan.extra_details) + ([reference_hint] if reference_hint else []),
                )
        return fallback_plan or PromptPlan(scene="diary moment")

    def plan(self, diary_text: str, reference_image=None, fallback_plan: PromptPlan | None = None) -> PromptPlan:
        if not diary_text.strip():
            return fallback_plan or PromptPlan(scene="diary moment")

        mode = self._resolve_mode()
        if mode == "rule_based":
            return fallback_plan or PromptPlan(scene="diary moment")
        if mode == "template":
            return self._template_plan(diary_text, reference_image=reference_image, fallback_plan=fallback_plan)
        if not SETTINGS.openai_enabled or not SETTINGS.openai_api_key or OpenAI is None:
            return fallback_plan or PromptPlan(scene="diary moment")

        client = OpenAI(api_key=SETTINGS.openai_api_key)
        reference_hint = extract_reference_hint(reference_image)

        response = client.responses.create(
            model=SETTINGS.openai_model,
            input=(
                "You are planning a compact image prompt for a Stable Diffusion diary illustration.\n"
                "Return strict JSON with keys: scene, subjects, mood, composition, extra_details.\n"
                "Rules:\n"
                "- Keep values concise and visual.\n"
                "- scene: short phrase for the main environment.\n"
                "- subjects: array of 2 to 5 concrete visual subjects.\n"
                "- mood: short comma-separated atmosphere phrase.\n"
                "- composition: short composition hint.\n"
                "- extra_details: array of 1 to 3 extra visual cues.\n"
                "- Preserve Korean meaning, but output visual planning terms in English.\n"
                "- Do not mention model names, LoRA names, or camera settings.\n\n"
                f"Diary text:\n{diary_text.strip()}\n\n"
                f"Reference hint:\n{reference_hint or 'none'}"
            ),
        )
        try:
            payload = json.loads(response.output_text)
            return PromptPlan(
                scene=str(payload.get("scene") or "").strip() or (fallback_plan.scene if fallback_plan else "diary moment"),
                subjects=[str(item).strip() for item in payload.get("subjects", []) if str(item).strip()],
                mood=str(payload.get("mood") or "").strip() or (fallback_plan.mood if fallback_plan else "calm, intimate, diary-like"),
                composition=str(payload.get("composition") or "").strip(),
                extra_details=[str(item).strip() for item in payload.get("extra_details", []) if str(item).strip()],
            )
        except Exception:
            return fallback_plan or PromptPlan(scene="diary moment")
