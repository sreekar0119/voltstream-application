from __future__ import annotations

import asyncio
import os
from functools import lru_cache
from typing import TYPE_CHECKING

import google.generativeai as genai

from app.core.config import settings
from app.services.chroma_service import get_collection

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


UNKNOWN_ANSWER = "I don't have that information in the provided documents."


@lru_cache(maxsize=1)
def _embedding_model() -> "SentenceTransformer":
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _embedding_model()
    embeddings = await asyncio.to_thread(
        model.encode,
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embeddings.tolist()


async def answer_from_documents(question: str) -> dict:
    collection = get_collection()
    if collection.count() == 0:
        return {"answer": UNKNOWN_ANSWER, "sources": []}

    query_embedding = (await embed_texts([question]))[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=settings.rag_top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    if not documents:
        return {"answer": UNKNOWN_ANSWER, "sources": []}

    context_blocks = []
    sources = []
    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) else {}
        source = metadata.get("source", "document")
        sources.append(source)
        context_blocks.append(f"[{source}]\n{document}")

    prompt = f"""
You are VoltStream PDF Q&A. Answer the user's question using ONLY the provided PDF context.
If the answer is not explicitly supported by the context, return exactly:
{UNKNOWN_ANSWER}

PDF context:
{chr(10).join(context_blocks)}

Question: {question}
""".strip()

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        settings.gemini_model,
        system_instruction="You are a strict document-grounded assistant.",
    )

    response = await asyncio.to_thread(
        model.generate_content,
        prompt,
        generation_config={"temperature": 0, "max_output_tokens": 1024},
    )
    
    answer = (response.text or "").strip()
    if not answer:
        answer = UNKNOWN_ANSWER

    return {"answer": answer, "sources": sorted(set(sources))}
