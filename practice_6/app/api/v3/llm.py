import time
from fastapi import APIRouter
from app.models.schemas import TextPredictIn, TextPredictOut

router = APIRouter(prefix="/api/v2", tags=["LLM"])

@router.post("/predict-text", response_model=TextPredictOut)
async def predict_text(req: TextPredictIn) -> TextPredictOut:
    """
    Принимает текст и возвращает заглушку ответа языковой модели.
    """
    t0 = time.perf_counter()

    # Заглушка генерации
    reply = f"Модель отвечает на: {req.prompt}»"
    dt = (time.perf_counter() - t0) * 1000.0
    
    return TextPredictOut(
        reply=reply,
        model_version="demo-llm-v1",
        latency_ms=round(dt, 3),
    )
