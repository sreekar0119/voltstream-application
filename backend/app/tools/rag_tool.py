from __future__ import annotations

from typing import Any

from app.services.rag_service import UNKNOWN_ANSWER, answer_from_context, retrieve_document_context


async def query_energy_documents(query: str) -> dict[str, Any]:
    """Search VoltStream's indexed energy PDFs for document-grounded optimization guidance."""
    if not query.strip():
        return {
            "ok": False,
            "answer": UNKNOWN_ANSWER,
            "sources": [],
            "context": [],
            "message": "A non-empty query is required to search the energy document knowledge base.",
        }

    retrieval = await retrieve_document_context(query)
    if not retrieval["ok"]:
        return {
            "ok": False,
            "answer": UNKNOWN_ANSWER,
            "sources": [],
            "context": [],
            "message": retrieval["message"],
        }

    answer = await answer_from_context(query, retrieval)
    return {
        "ok": True,
        "query": query,
        "answer": answer["answer"],
        "sources": answer["sources"],
        "context": retrieval["context"],
        "message": retrieval["message"],
    }
