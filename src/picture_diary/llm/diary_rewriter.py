from __future__ import annotations

from dataclasses import dataclass

from picture_diary.config import SETTINGS

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency at runtime
    OpenAI = None


@dataclass
class DiaryRewriter:
    """Optional LLM stage.

    If an API key is unavailable, the original text is returned unchanged.
    """

    def rewrite(self, raw_diary: str) -> str:
        text = raw_diary.strip()
        if not text:
            return ""

        if not SETTINGS.openai_enabled or not SETTINGS.openai_api_key or OpenAI is None:
            return text

        client = OpenAI(api_key=SETTINGS.openai_api_key)
        response = client.responses.create(
            model=SETTINGS.openai_model,
            input=(
                "Rewrite the following diary into a concise first-person diary entry. "
                "Keep the original meaning, preserve Korean when the input is Korean, "
                "and stay within about 120 characters if possible.\n\n"
                f"Diary:\n{text}"
            ),
        )
        return response.output_text.strip() or text
