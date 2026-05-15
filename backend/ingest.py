from __future__ import annotations

import asyncio
import hashlib
import sys
from pathlib import Path

import tiktoken
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from app.core.config import settings  # noqa: E402
from app.services.chroma_service import reset_collection  # noqa: E402
from app.services.rag_service import embed_texts  # noqa: E402


def _chunks(text: str, chunk_tokens: int = 420, overlap_tokens: int = 60) -> list[str]:
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_tokens
        chunk = encoding.decode(tokens[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap_tokens
    return chunks


def _load_pdf_chunks(pdf_path: Path) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    records = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for chunk_index, chunk in enumerate(_chunks(text), start=1):
            chunk_hash = hashlib.sha256(
                f"{pdf_path.name}:{page_index}:{chunk_index}:{chunk}".encode("utf-8")
            ).hexdigest()[:24]
            records.append(
                {
                    "id": chunk_hash,
                    "document": chunk,
                    "metadata": {
                        "source": pdf_path.name,
                        "page": page_index,
                        "chunk": chunk_index,
                    },
                }
            )
    return records


async def ingest_documents() -> None:
    settings.documents_dir.mkdir(parents=True, exist_ok=True)
    pdf_paths = sorted(settings.documents_dir.glob("*.pdf"))

    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        print("GEMINI_API_KEY is missing. Add a valid key to backend/.env before running ingest.py.")
        return

    if not pdf_paths:
        print(f"No PDFs found in {settings.documents_dir}.")
        return

    records = []
    for pdf_path in pdf_paths:
        records.extend(_load_pdf_chunks(pdf_path))

    if not records:
        print("PDFs were found, but no extractable text was available.")
        return

    collection = reset_collection()

    batch_size = 64
    for start in range(0, len(records), batch_size):
        batch = records[start : start + batch_size]
        batch_number = (start // batch_size) + 1
        total_batches = (len(records) + batch_size - 1) // batch_size
        print(f"Embedding batch {batch_number}/{total_batches}...")
        try:
            embeddings = await asyncio.wait_for(
                embed_texts([record["document"] for record in batch], task_type="retrieval_document"),
                timeout=90,
            )
        except TimeoutError:
            print("Gemini embedding request timed out. Check your network connection and try again.")
            return
        except Exception as exc:
            print(f"Gemini embedding request failed: {exc}")
            return
        collection.add(
            ids=[record["id"] for record in batch],
            documents=[record["document"] for record in batch],
            metadatas=[record["metadata"] for record in batch],
            embeddings=embeddings,
        )

    print(f"Ingested {len(records)} chunks from {len(pdf_paths)} PDF file(s).")


if __name__ == "__main__":
    try:
        asyncio.run(ingest_documents())
    except KeyboardInterrupt:
        print("Ingestion cancelled.")
