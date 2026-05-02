from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
DEFAULT_MODEL = "qwen-plus"
DEFAULT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"


def _read_env_file() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_PATH.exists():
        return values

    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


_ENV_CACHE = _read_env_file()


def _env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name) or _ENV_CACHE.get(name) or default


def _format_context(context: dict[str, Any]) -> str:
    if not context:
        return "无额外实验上下文。"

    lines: list[str] = []
    for key, value in context.items():
        if isinstance(value, (dict, list)):
            shown = json.dumps(value, ensure_ascii=False)
        else:
            shown = str(value)
        lines.append(f"- {key}: {shown}")
    return "\n".join(lines)


def _extract_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError("千问返回内容为空。")

    message = choices[0].get("message") or {}
    content = message.get("content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        texts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(str(item.get("text", "")).strip())
        joined = "\n".join(part for part in texts if part)
        if joined:
            return joined

    raise RuntimeError("无法解析千问返回的答案。")


def ask_ai_tutor(question: str, module: str = "general", context: dict[str, Any] | None = None) -> str:
    api_key = _env("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("未在 .env 中找到 DASHSCOPE_API_KEY。")

    endpoint = _env("DASHSCOPE_CHAT_URL", DEFAULT_URL)
    model = _env("DASHSCOPE_MODEL", DEFAULT_MODEL)
    context_block = _format_context(context or {})

    system_prompt = (
        "你是 Fourier Blue Lab 的内置 AI 助教。"
        "你的任务是帮助本科生理解傅里叶级数、傅里叶积分、傅里叶变换、频域滤波和图像加噪实验。"
        "回答要求简洁、准确、面向课堂演示；优先结合用户当前实验参数来解释。"
        "如果用户 asking for steps，就直接给步骤；如果 asking for concept，就先给结论再解释。"
        "不要编造未提供的数据。"
    )

    user_prompt = (
        f"当前模块：{module}\n"
        f"当前实验上下文：\n{context_block}\n\n"
        f"用户问题：{question}"
    )

    payload = {
        "model": model,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"千问接口报错：HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"无法连接千问接口：{exc.reason}") from exc

    data = json.loads(body)
    if "error" in data:
        message = data["error"].get("message", "未知错误")
        raise RuntimeError(f"千问接口返回错误：{message}")

    return _extract_text(data)
