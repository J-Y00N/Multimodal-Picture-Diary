from PIL import Image

from picture_diary.compose.page_template import compose_diary_page


def test_compose_diary_page_returns_expected_canvas_size() -> None:
    generated = Image.new("RGB", (512, 512), color="navy")
    page = compose_diary_page(
        diary_text="오늘은 하늘이 맑아서 기분이 좋았다.",
        generated_image=generated,
        prompt="msl monet, personal diary illustration",
    )
    assert page.size == (1080, 1520)


def test_compose_diary_page_supports_debug_prompt_notes() -> None:
    generated = Image.new("RGB", (512, 512), color="navy")
    page = compose_diary_page(
        diary_text="오늘은 하늘이 맑아서 기분이 좋았다.",
        generated_image=generated,
        prompt="msl monet, personal diary illustration",
        show_prompt_notes=True,
    )
    assert page.size == (1080, 1520)
