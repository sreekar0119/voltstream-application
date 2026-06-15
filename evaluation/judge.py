from __future__ import annotations

import asyncio
import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"

import sys

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings


def configure_evaluation_credentials() -> None:
    """Use an absolute credentials path when evaluation runs outside backend/."""
    if settings.google_application_credentials:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(
            settings.google_application_credentials.resolve()
        )


@lru_cache(maxsize=1)
def _vertex_client():
    if not settings.vertex_ai_project:
        raise RuntimeError("VERTEX_AI_PROJECT or GOOGLE_CLOUD_PROJECT is not configured.")

    configure_evaluation_credentials()

    from google import genai

    return genai.Client(
        vertexai=True,
        project=settings.vertex_ai_project,
        location=settings.vertex_ai_location,
    )


def _context_text(chunks: list[dict[str, Any]]) -> str:
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        source = chunk.get("source") or "document"
        page = (chunk.get("metadata") or {}).get("page")
        label = f"{source}, page {page}" if page else source
        blocks.append(f"[Chunk {index}: {label}]\n{chunk.get('text', '')}")
    return "\n\n".join(blocks)


def _parse_judge_json(text: str) -> dict[str, str]:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()
    elif not cleaned.startswith("{"):
        json_object = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if json_object:
            cleaned = json_object.group(0).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        faithfulness_match = re.search(
            r'"faithfulness"\s*:\s*"(PASS|FAIL)"',
            cleaned,
            flags=re.IGNORECASE,
        )
        relevance_match = re.search(
            r'"relevance"\s*:\s*"(PASS|FAIL)"',
            cleaned,
            flags=re.IGNORECASE,
        )
        if faithfulness_match and relevance_match:
            reason_match = re.search(
                r'"reason"\s*:\s*"([^"]*)',
                cleaned,
                flags=re.IGNORECASE | re.DOTALL,
            )
            return {
                "faithfulness": faithfulness_match.group(1).upper(),
                "relevance": relevance_match.group(1).upper(),
                "reason": (
                    reason_match.group(1).strip()
                    if reason_match
                    else "Recovered PASS/FAIL labels from malformed judge JSON."
                ),
            }
        return {
            "faithfulness": "FAIL",
            "relevance": "FAIL",
            "reason": f"Judge returned non-JSON output: {text[:180]}",
        }

    faithfulness = str(data.get("faithfulness", "FAIL")).upper()
    relevance = str(data.get("relevance", "FAIL")).upper()
    return {
        "faithfulness": "PASS" if faithfulness == "PASS" else "FAIL",
        "relevance": "PASS" if relevance == "PASS" else "FAIL",
        "reason": str(data.get("reason", "")).strip(),
    }


async def judge_answer(question: str, answer: str, chunks: list[dict[str, Any]]) -> dict[str, str]:
    from google.genai import types

    prompt = f"""
You are an evaluator for a RAG system. Judge the generated answer using only the retrieved context.

Question:
{question}

Retrieved Context:
{_context_text(chunks)}

Generated Answer:
{answer}

Evaluate:
1. Faithfulness: PASS if the answer is supported by the retrieved context; FAIL if it contains unsupported claims.
2. Relevance: PASS if the answer directly addresses the question; FAIL otherwise.

Return only valid JSON in this exact shape:
{{
  "faithfulness": "PASS/FAIL",
  "relevance": "PASS/FAIL",
  "reason": "brief explanation under 25 words"
}}
""".strip()

    client = _vertex_client()
    response = await asyncio.to_thread(
        client.models.generate_content,
        model=settings.vertex_ai_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a strict RAG evaluation judge.",
            temperature=0,
            max_output_tokens=2048,
            response_mime_type="application/json",
        ),
    )
    return _parse_judge_json(response.text or "")
