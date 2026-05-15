from fastapi import APIRouter, HTTPException

from app.schemas.ai import QARequest, QAResponse
from app.services.rag_service import answer_from_documents

router = APIRouter(tags=["ai"])


@router.post("/qa", response_model=QAResponse)
async def qa(payload: QARequest) -> QAResponse:
    try:
        result = await answer_from_documents(payload.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return QAResponse(**result)