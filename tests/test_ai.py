import pytest

from fourier_lab import ai


def test_extract_text_supports_string_content() -> None:
    payload = {"choices": [{"message": {"content": "你好，傅里叶"}}]}
    assert ai._extract_text(payload) == "你好，傅里叶"


def test_ask_ai_tutor_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai, "_ENV_CACHE", {})
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.setattr(ai, "_read_streamlit_secret", lambda name: None)

    with pytest.raises(RuntimeError, match="DASHSCOPE_API_KEY"):
        ai.ask_ai_tutor("测试问题")
