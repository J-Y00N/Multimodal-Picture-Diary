from __future__ import annotations

from dataclasses import dataclass
import re

from picture_diary.config import SETTINGS
from picture_diary.diffusion.style_registry import get_style_spec
from picture_diary.llm.prompt_planner import PromptPlanner
from picture_diary.llm.prompt_types import PromptPlan
from picture_diary.multimodal.reference_image import extract_reference_hint


@dataclass
class PromptBuilder:
    planner: PromptPlanner | None = None
    keyword_map: tuple[tuple[tuple[str, ...], str], ...] = (
        (("하늘", "sky"), "open sky"),
        (("구름", "cloud"), "soft clouds"),
        (("건물", "빌딩", "architecture", "building"), "modern building"),
        (("거리", "길", "road", "street"), "quiet walkway"),
        (("공원", "산책", "park", "walk"), "park stroll"),
        (("나무", "tree"), "trees"),
        (("연못", "호수", "호숫가", "pond", "lake", "water"), "reflective water"),
        (("봄", "spring"), "spring air"),
        (("노을", "석양", "sunset"), "sunset glow"),
        (("밤", "밤에", "night"), "evening light"),
        (("비가", "빗", "rain"), "rainy atmosphere"),
        (("도시", "city"), "urban scene"),
        (("강", "river"), "riverside view"),
        (("바다", "sea", "ocean"), "coastal scenery"),
        (("산", "mountain"), "mountain backdrop"),
        (("꽃", "flower", "벚꽃"), "blooming flowers"),
        (("카페", "cafe", "coffee"), "cafe corner"),
        (("학교", "campus", "교실", "수업"), "campus moment"),
        (("도서관", "library"), "quiet library"),
        (("지하철", "subway", "버스", "bus", "기차", "train"), "commuter scene"),
        (("시장", "market"), "busy market"),
        (("축제", "festival", "공연", "concert"), "festive crowd"),
        (("친구", "friend"), "companionship"),
        (("가족", "family"), "family warmth"),
        (("고양이", "cat", "강아지", "dog", "반려"), "gentle companion"),
        (("사진", "camera"), "captured moment"),
        (("창문", "창가", "window"), "window light"),
        (("책", "book"), "reading pause"),
    )

    def _contains_trigger(self, text_lower: str, trigger: str) -> bool:
        if trigger.isascii():
            return re.search(rf"\b{re.escape(trigger)}\b", text_lower) is not None
        if len(trigger) <= 1:
            return False
        return trigger in text_lower

    def infer_mood(self, text: str) -> str:
        text_lower = text.lower()
        if any(self._contains_trigger(text_lower, token) for token in ["행복", "즐거", "기쁘", "happy", "joy"]):
            return "warm, joyful, reflective"
        if any(self._contains_trigger(text_lower, token) for token in ["슬프", "우울", "sad", "lonely"]):
            return "quiet, melancholic, introspective"
        if any(self._contains_trigger(text_lower, token) for token in ["설레", "두근", "excited", "anticipat"]):
            return "hopeful, tender, luminous"
        if any(self._contains_trigger(text_lower, token) for token in ["공부", "study", "work", "바쁘", "업무"]):
            return "focused, thoughtful, grounded"
        if any(self._contains_trigger(text_lower, token) for token in ["비가", "빗", "rain", "밤", "night"]):
            return "moody, atmospheric, cinematic"
        return "calm, intimate, diary-like"

    def _fallback_terms(self, text: str) -> list[str]:
        compact = re.sub(r"\s+", " ", text).strip()
        if not compact:
            return []

        english_terms = re.findall(r"[a-zA-Z]{3,}", compact.lower())
        korean_terms = re.findall(r"[가-힣]{2,}", compact)
        raw_terms = english_terms + korean_terms

        cleaned: list[str] = []
        stopwords = {"오늘", "어제", "그리고", "그래서", "정말", "조금", "잠시", "아주", "the", "and", "with"}
        for term in raw_terms:
            if term in stopwords:
                continue
            if term not in cleaned:
                cleaned.append(term)
            if len(cleaned) >= 4:
                break
        return cleaned

    def extract_scene_keywords(self, text: str) -> list[str]:
        text_lower = text.lower()
        keywords: list[str] = []
        for triggers, label in self.keyword_map:
            if any(self._contains_trigger(text_lower, trigger) for trigger in triggers):
                if label not in keywords:
                    keywords.append(label)
            if len(keywords) >= 6:
                break

        if keywords:
            return keywords

        fallback_terms = self._fallback_terms(text)
        if fallback_terms:
            return fallback_terms

        compact = re.sub(r"\s+", " ", text).strip()
        fallback = compact[: SETTINGS.max_prompt_chars].strip(" ,.")
        return [fallback] if fallback else []

    def rule_based_plan(self, diary_text: str, reference_image=None) -> PromptPlan:
        scene_keywords = self.extract_scene_keywords(diary_text)
        reference_hint = extract_reference_hint(reference_image)
        scene = scene_keywords[0] if scene_keywords else "diary moment"
        subjects = scene_keywords[1:5]
        extra_details = ["painterly", "cohesive scene"]
        if reference_hint:
            extra_details.append(reference_hint)
        return PromptPlan(
            scene=scene,
            subjects=subjects,
            mood=self.infer_mood(diary_text),
            composition=reference_hint,
            extra_details=extra_details,
        )

    def build(self, diary_text: str, style_key: str, reference_image=None) -> str:
        spec = get_style_spec(style_key)
        fallback_plan = self.rule_based_plan(diary_text, reference_image=reference_image)
        plan = (
            self.planner.plan(diary_text, reference_image=reference_image, fallback_plan=fallback_plan)
            if self.planner is not None
            else fallback_plan
        )
        prompt_parts = [plan.scene] + plan.subjects

        parts = [
            spec.trigger,
            spec.style_note,
            plan.mood,
            "diary illustration",
            ", ".join(part for part in prompt_parts if part),
        ]
        if plan.composition:
            parts.append(plan.composition)
        if plan.extra_details:
            parts.append(", ".join(plan.extra_details))
        return ", ".join(part for part in parts if part)
