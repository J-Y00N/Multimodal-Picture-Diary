import pytest

from picture_diary.diffusion.style_registry import get_quality_preset, get_style_spec


def test_get_style_spec_returns_style() -> None:
    assert get_style_spec("monet").trigger == "msl monet"


def test_get_style_spec_rejects_unknown_style() -> None:
    with pytest.raises(ValueError):
        get_style_spec("unknown-style")


def test_get_quality_preset_returns_expected_defaults() -> None:
    preset = get_quality_preset("monet", "balanced")
    assert preset.width == 768
    assert preset.steps == 28


def test_get_quality_preset_rejects_unknown_preset() -> None:
    with pytest.raises(ValueError):
        get_quality_preset("monet", "unknown-preset")
