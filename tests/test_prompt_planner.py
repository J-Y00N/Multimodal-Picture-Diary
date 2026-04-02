from picture_diary.llm.prompt_builder import PromptBuilder
from picture_diary.llm.prompt_planner import PromptPlanner
from picture_diary.llm.prompt_types import PromptPlan


def test_prompt_planner_falls_back_without_openai() -> None:
    planner = PromptPlanner(mode="openai")
    fallback = PromptPlan(
        scene="quiet library",
        subjects=["bookshelves", "reading desk"],
        mood="focused, thoughtful, grounded",
        composition="",
        extra_details=["painterly"],
    )
    plan = planner.plan("도서관에서 책을 읽었다.", fallback_plan=fallback)
    assert plan.scene == "quiet library"


def test_prompt_builder_uses_rule_based_plan_without_planner() -> None:
    builder = PromptBuilder()
    prompt = builder.build("도서관에서 책을 읽으며 창가에 앉아 있었다.", "monet")
    assert "quiet library" in prompt
    assert "reading pause" in prompt or "window light" in prompt


def test_prompt_planner_template_mode_returns_preset_plan() -> None:
    planner = PromptPlanner(mode="template")
    plan = planner.plan("도서관에서 책을 읽으며 공부했다.")
    assert plan.scene == "quiet library interior"
    assert "bookshelves" in plan.subjects
