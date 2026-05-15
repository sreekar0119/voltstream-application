from __future__ import annotations

import os

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_TELEMETRY", "False")

import chromadb
from chromadb.config import Settings

from app.core.config import settings


def _client():
    return chromadb.PersistentClient(
        path=str(settings.chroma_db_dir),
        settings=Settings(anonymized_telemetry=False),
    )


def get_collection():
    settings.chroma_db_dir.mkdir(parents=True, exist_ok=True)
    client = _client()
    return client.get_or_create_collection(
        name=settings.rag_collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def reset_collection():
    settings.chroma_db_dir.mkdir(parents=True, exist_ok=True)
    client = _client()
    try:
        client.delete_collection(settings.rag_collection_name)
    except ValueError:
        pass
    return client.get_or_create_collection(
        name=settings.rag_collection_name,
        metadata={"hnsw:space": "cosine"},
    )
