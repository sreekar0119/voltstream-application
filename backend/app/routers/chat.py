from fastapi import APIRouter, HTTPException

from app.schemas.ai import ChatRequest, ChatResponse
from app.services.gemini_service import generate_energy_answer

router = APIRouter(tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    clean_message = request.message.strip()

    if not clean_message:
        raise HTTPException(status_code=422, detail="Message is required.")

    try:
        answer = await generate_energy_answer(clean_message)
        return ChatResponse(answer=answer, mode="chat")
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
