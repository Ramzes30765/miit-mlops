import time

from fastapi import APIRouter

from app.models.schemas import TextPredictIn, TextPredictOut

router = APIRouter(tags=["Text API demo"])


@router.post("/predict-text", response_model=TextPredictOut)
def predict_text(req: TextPredictIn) -> TextPredictOut:
    """Принимает текст и возвращает демонстрационный ответ без вызова модели."""
    t0 = time.perf_counter()

    reply = f"Модель отвечает на запрос: {req.prompt}"
    dt = (time.perf_counter() - t0) * 1000.0

    return TextPredictOut(
        reply=reply,
        model_version="demo-llm-v1",
        latency_ms=round(dt, 3),
    )
