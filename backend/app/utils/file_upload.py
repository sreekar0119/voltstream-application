from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import UploadFile


MAX_CHAT_PDF_SIZE_BYTES = 10 * 1024 * 1024
CHAT_PDF_MIME_TYPES = {"application/pdf", "application/x-pdf"}


class FileValidationError(ValueError):
    pass


def validate_pdf_metadata(file: UploadFile) -> None:
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise FileValidationError("Only PDF files are allowed.")

    if file.content_type and file.content_type not in CHAT_PDF_MIME_TYPES:
        raise FileValidationError("Only PDF files are allowed.")


async def save_upload_to_temp_pdf(file: UploadFile) -> Path:
    validate_pdf_metadata(file)

    size = 0
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_path = Path(temp.name)

    try:
        with temp:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_CHAT_PDF_SIZE_BYTES:
                    raise FileValidationError("PDF must be 10MB or smaller.")
                temp.write(chunk)

        if size == 0:
            raise FileValidationError("Uploaded PDF is empty.")

        return temp_path
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
