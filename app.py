from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from fourier_lab.ai import ask_ai_tutor
from fourier_lab.analysis import (
    fourier_series_demo,
    image_demo,
    quiz_questions,
    series_to_integral_demo,
    transform_demo,
)


BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Fourier Blue Lab", version="2.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class AIChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    module: Literal["general", "series", "transition", "transform", "image"] = "general"
    context: dict[str, Any] = Field(default_factory=dict)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "quiz_questions": quiz_questions(),
        },
    )


@app.get("/api/series")
async def api_series(terms: int = Query(6, ge=1, le=12)) -> dict[str, object]:
    return fourier_series_demo(terms)


@app.get("/api/transition")
async def api_transition(period: float = Query(16.0, ge=6.0, le=28.0)) -> dict[str, object]:
    return series_to_integral_demo(period)


@app.get("/api/transform")
async def api_transform(
    signal: str = Query("sensor", pattern="^(sensor|pulse|chirp)$"),
    noise: float = Query(0.4, ge=0.0, le=1.2),
    cutoff: float = Query(1.8, ge=0.2, le=5.5),
    mode: str = Query("lowpass", pattern="^(lowpass|highpass|bandpass)$"),
) -> dict[str, object]:
    return transform_demo(signal, noise, cutoff, mode)


@app.get("/api/image-demo")
async def api_image_demo(
    mode: str = Query("lowpass", pattern="^(lowpass|highpass)$"),
    cutoff: int = Query(40, ge=6, le=96),
    noise: float = Query(0.16, ge=0.0, le=0.32),
) -> dict[str, object]:
    return image_demo(mode, cutoff, noise)


@app.post("/api/ai/chat")
async def api_ai_chat(payload: AIChatRequest) -> dict[str, str]:
    try:
        answer = ask_ai_tutor(
            question=payload.question,
            module=payload.module,
            context=payload.context,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive path
        raise HTTPException(status_code=500, detail=f"AI 服务调用失败：{exc}") from exc

    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
