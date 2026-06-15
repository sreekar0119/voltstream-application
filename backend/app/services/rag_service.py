from __future__ import annotations

import asyncio
import os
from functools import lru_cache
from typing import TYPE_CHECKING

from app.core.config import settings
from app.services.chroma_service import get_collection

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer
    from google.genai import Client


UNKNOWN_ANSWER = "I don't have that information in the provided documents."


@lru_cache(maxsize=1)
def _embedding_model() -> "SentenceTransformer":
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


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


async def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _embedding_model()
    embeddings = await asyncio.to_thread(
        model.encode,
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embeddings.tolist()


async def retrieve_document_context(question: str) -> dict:
    """Retrieve grounded PDF context from the existing Chroma collection."""
    collection = get_collection()
    if collection.count() == 0:
        return {
            "ok": False,
            "query": question,
            "context": [],
            "sources": [],
            "message": UNKNOWN_ANSWER,
        }

    query_embedding = (await embed_texts([question]))[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=settings.rag_top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]
    if not documents:
        return {
            "ok": False,
            "query": question,
            "context": [],
            "sources": [],
            "message": UNKNOWN_ANSWER,
        }

    context_blocks = []
    sources = []
    context = []
    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) else {}
        source = metadata.get("source", "document")
        sources.append(source)
        context_blocks.append(f"[{source}]\n{document}")
        context.append(
            {
                "id": ids[index] if index < len(ids) else None,
                "source": source,
                "text": document,
                "metadata": metadata,
                "distance": distances[index] if index < len(distances) else None,
            }
        )

    return {
        "ok": True,
        "query": question,
        "context": context,
        "context_text": "\n\n".join(context_blocks),
        "sources": sorted(set(sources)),
        "message": f"Retrieved {len(context)} document chunks from the VoltStream energy knowledge base.",
    }


async def answer_from_context(question: str, retrieval: dict) -> dict:
    if not retrieval["ok"]:
        return {"answer": UNKNOWN_ANSWER, "sources": []}

    prompt = f"""
You are VoltStream PDF Q&A. Answer the user's question using ONLY the provided PDF context.
If the answer is not explicitly supported by the context, return exactly:
{UNKNOWN_ANSWER}

PDF context:
{retrieval["context_text"]}

Question: {question}
""".strip()

    from google.genai import types

    client = _vertex_client()
    response = await asyncio.to_thread(
        client.models.generate_content,
        model=settings.vertex_ai_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a strict document-grounded assistant.",
            temperature=0,
            max_output_tokens=1024,
        ),
    )
    
    answer = (response.text or "").strip()
    if not answer:
        answer = UNKNOWN_ANSWER

    return {"answer": answer, "sources": retrieval["sources"]}


async def answer_from_documents(question: str) -> dict:
    retrieval = await retrieve_document_context(question)
    return await answer_from_context(question, retrieval)
