from picture_diary.llm.prompt_builder import PromptBuilder


def test_prompt_contains_style_trigger() -> None:
    builder = PromptBuilder()
    prompt = builder.build("오늘은 산책을 했다.", "monet")
    assert "msl monet" in prompt


def test_prompt_contains_reference_hint() -> None:
    from PIL import Image

    builder = PromptBuilder()
    reference = Image.new("RGB", (640, 480), color="white")
    prompt = builder.build("노을을 보며 걸었다.", "animate_landscape", reference_image=reference)
    assert "reference image provided" in prompt


def test_prompt_extracts_scene_keywords() -> None:
    builder = PromptBuilder()
    prompt = builder.build("봄 하늘 아래 건물 앞을 산책하며 나무와 연못을 바라보았다.", "monet")
    assert "open sky" in prompt
    assert "modern building" in prompt
    assert "park stroll" in prompt or "trees" in prompt


def test_prompt_extracts_diverse_place_keywords() -> None:
    builder = PromptBuilder()
    prompt = builder.build("비 오는 밤에 카페 창가에서 책을 읽다가 지하철을 타고 집에 돌아왔다.", "monet")
    assert "cafe corner" in prompt
    assert "window light" in prompt
    assert "commuter scene" in prompt


def test_prompt_uses_clean_fallback_terms_when_no_keyword_matches() -> None:
    builder = PromptBuilder()
    prompt = builder.build("오늘은 메모 정리를 하며 prototype review를 준비했다.", "monet")
    assert "prototype" in prompt or "메모" in prompt
