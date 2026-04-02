from picture_diary.llm.diary_rewriter import DiaryRewriter


def test_rewriter_returns_input_when_disabled() -> None:
    rewriter = DiaryRewriter()
    text = "오늘은 조용한 하루였다."
    assert rewriter.rewrite(text) == text
