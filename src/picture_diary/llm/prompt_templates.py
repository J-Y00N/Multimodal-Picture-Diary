from __future__ import annotations

from dataclasses import dataclass

from picture_diary.llm.prompt_types import PromptPlan


@dataclass(frozen=True)
class PromptTemplate:
    key: str
    triggers: tuple[str, ...]
    plan: PromptPlan


PROMPT_TEMPLATES: tuple[PromptTemplate, ...] = (
    PromptTemplate(
        key="library_study",
        triggers=("도서관", "library", "책", "공부", "study"),
        plan=PromptPlan(
            scene="quiet library interior",
            subjects=["bookshelves", "reading desk", "window light"],
            mood="focused, thoughtful, grounded",
            composition="calm indoor composition",
            extra_details=["soft paper textures", "still atmosphere"],
        ),
    ),
    PromptTemplate(
        key="urban_walk",
        triggers=("건물", "도시", "거리", "산책", "building", "city", "street"),
        plan=PromptPlan(
            scene="urban walkway",
            subjects=["modern building", "open sky", "pedestrian path"],
            mood="calm, intimate, diary-like",
            composition="wide street-level composition",
            extra_details=["gentle painterly texture"],
        ),
    ),
    PromptTemplate(
        key="cafe_reflection",
        triggers=("카페", "coffee", "창가", "window", "대화"),
        plan=PromptPlan(
            scene="quiet cafe corner",
            subjects=["window light", "small table", "warm drink"],
            mood="warm, reflective, tender",
            composition="cozy mid-shot composition",
            extra_details=["soft ambient light"],
        ),
    ),
    PromptTemplate(
        key="travel_landscape",
        triggers=("여행", "바다", "산", "river", "sea", "travel"),
        plan=PromptPlan(
            scene="travel landscape",
            subjects=["distant horizon", "expansive sky", "natural scenery"],
            mood="hopeful, luminous, reflective",
            composition="wide scenic composition",
            extra_details=["memory-like atmosphere"],
        ),
    ),
)
