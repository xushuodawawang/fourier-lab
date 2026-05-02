import json

import pytest

from fourier_lab import ai


class FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self) -> bytes:
        return self.payload


def test_extract_text_supports_string_content() -> None:
    payload = {"choices": [{"message": {"content": "你好，傅里叶"}}]}
    assert ai._extract_text(payload) == "你好，傅里叶"


def test_has_ai_credentials_accepts_explicit_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai, "_ENV_CACHE", {})
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.setattr(ai, "_read_streamlit_secret", lambda name: None)
    assert ai.has_ai_credentials("demo-key")


def test_ask_ai_tutor_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai, "_ENV_CACHE", {})
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.setattr(ai, "_read_streamlit_secret", lambda name: None)

    with pytest.raises(RuntimeError, match="DASHSCOPE_API_KEY"):
        ai.ask_ai_tutor("测试问题")


def test_ask_ai_tutor_accepts_runtime_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai, "_ENV_CACHE", {})
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.setattr(ai, "_read_streamlit_secret", lambda name: None)

    captured: dict[str, str | None] = {}

    def fake_urlopen(request, timeout: int) -> FakeResponse:
        headers = {key.lower(): value for key, value in request.header_items()}
        captured["authorization"] = headers.get("authorization")
        payload = {"choices": [{"message": {"content": "连接成功"}}]}
        return FakeResponse(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(ai.urllib.request, "urlopen", fake_urlopen)

    answer = ai.ask_ai_tutor(
        "测试问题",
        api_key="demo-key",
        model="qwen-plus",
    )

    assert answer == "连接成功"
    assert captured["authorization"] == "Bearer demo-key"
