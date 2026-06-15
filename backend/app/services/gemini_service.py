from __future__ import annotations

import asyncio
import os
from functools import lru_cache
from typing import TYPE_CHECKING

from app.core.config import settings

if TYPE_CHECKING:
    from google.genai import Client


SYSTEM_PROMPT = """
You are a general conversational assistant that can answer anything.
""".strip()


def _extract_text(response) -> str:
    try:
        return (response.text or "").strip()
    except ValueError:
        pass

    chunks = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            text = getattr(part, "text", "")
            if text:
                chunks.append(text)
    return "\n".join(chunks).strip()

def _empty_response_reason(response) -> str:
    prompt_feedback = getattr(response, "prompt_feedback", None)
    block_reason = getattr(prompt_feedback, "block_reason", None)
    if block_reason:
        return f"Vertex AI blocked the prompt before generating text. Reason: {block_reason}."

    candidates = getattr(response, "candidates", []) or []
    if candidates:
         finish_reason = getattr(candidates[0], "finish_reason", None)
         reason_name = getattr(finish_reason, "name", None)
         reason_value = getattr(finish_reason, "value", finish_reason)
         reason = reason_name or str(reason_value)
         if reason == "MAX_TOKENS":
             return "Vertex AI stopped because the output token limit was reached before usable text was returned. Try a shorter question."
         if reason == "SAFETY":
             return "Vertex AI did not return text because the response was blocked by safety filters."
         return f"Vertex AI returned no text. Finish reason: {reason}."

    return "Vertex AI returned no text. Please try rephrasing the question."


@lru_cache(maxsize=1)
def _vertex_client() -> "Client":
    if not settings.vertex_ai_project:
        raise RuntimeError("VERTEX_AI_PROJECT or GOOGLE_CLOUD_PROJECT is not configured.")

    if settings.google_application_credentials:
        os.environ.setdefault(
            "GOOGLE_APPLICATION_CREDENTIALS",
            str(settings.google_application_credentials),
        )

    from google import genai

    return genai.Client(
        vertexai=True,
        project=settings.vertex_ai_project,
        location=settings.vertex_ai_location,
    )


"""async def _wait_for_uploaded_file(genai, uploaded_file, timeout_seconds: int = 60):
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    file = uploaded_file

    while True:
        state = getattr(getattr(file, "state", None), "name", None)
        if state in {None, "ACTIVE"}:
            return file
        if state == "FAILED":
            raise RuntimeError("Gemini could not process the uploaded PDF.")
        if asyncio.get_running_loop().time() >= deadline:
            raise RuntimeError("Gemini timed out while processing the uploaded PDF.")

        await asyncio.sleep(1)
        file = await asyncio.to_thread(genai.get_file, uploaded_file.name)"""


async def generate_energy_answer(message: str) -> str:
    from google.genai import types

    client = _vertex_client()
    response = await asyncio.to_thread(
        client.models.generate_content,
        model=settings.vertex_ai_model,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.45,
            max_output_tokens=500,
        ),
    )

    answer = _extract_text(response)
    return answer or _empty_response_reason(response)


"""async def generate_answer_from_pdf(message: str, pdf_path: Path, display_name: str) -> str:
    genai = _configure_genai()
    model = _build_model(genai)
    uploaded_file = None

    try:
        uploaded_file = await asyncio.to_thread(
            genai.upload_file,
            path=str(pdf_path),
            display_name=display_name,
            mime_type="application/pdf",
        )
        uploaded_file = await _wait_for_uploaded_file(genai, uploaded_file)

        response = await asyncio.to_thread(
            model.generate_content,
            [
                uploaded_file,
                (
                    "Read the attached PDF directly and answer the user's question in natural "
                    "language. If the answer is not supported by the PDF, say that clearly.\n\n"
                    f"Question: {message}"
                ),
            ],
            generation_config={"temperature": 0.35, "max_output_tokens": 2048},
        )

        answer = _extract_text(response)
        return answer or _empty_response_reason(response)
    except Exception as exc:
        raise RuntimeError(f"Gemini PDF analysis failed: {exc}") from exc
    finally:
        if uploaded_file is not None:
            try:
                await asyncio.to_thread(genai.delete_file, uploaded_file.name)
            except Exception:
                pass"""
