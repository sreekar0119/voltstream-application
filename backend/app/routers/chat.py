from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.ai import ChatResponse
from app.services.gemini_service import generate_answer_from_pdf, generate_energy_answer
from app.utils.file_upload import FileValidationError, save_upload_to_temp_pdf

router = APIRouter(tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: Annotated[str, Form(..., min_length=1, max_length=4000)],
    file: Annotated[UploadFile | None, File()] = None,
) -> ChatResponse:
    temp_path: Path | None = None
    clean_message = message.strip()

    if not clean_message:
        raise HTTPException(status_code=422, detail="Message is required.")

    try:
        if file is None:
            answer = await generate_energy_answer(clean_message)
            return ChatResponse(answer=answer, mode="chat")

        temp_path = await save_upload_to_temp_pdf(file)
        answer = await generate_answer_from_pdf(
            clean_message,
            temp_path,
            file.filename or "uploaded.pdf",
        )
        return ChatResponse(answer=answer, mode="pdf", file_name=file.filename)
    except FileValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
