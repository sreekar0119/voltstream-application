from __future__ import annotations

import asyncio
import hashlib
import sys
from pathlib import Path

import tiktoken
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from app.core.config import settings  
from app.services.chroma_service import reset_collection  
from app.services.rag_service import embed_texts  


def _chunks(text: str, chunk_tokens: int, overlap_tokens: int) -> list[str]:
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
    chunk_tokens = settings.rag_chunk_tokens
    overlap_tokens = settings.rag_chunk_overlap
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for chunk_index, chunk in enumerate(
            _chunks(text, chunk_tokens=chunk_tokens, overlap_tokens=overlap_tokens),
            start=1,
        ):
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
                embed_texts([record["document"] for record in batch]),
                timeout=90,
            )
        except TimeoutError:
            print("Embedding request timed out. Check your system load and try again.")
            return
        except Exception as exc:
            print(f"Embedding request failed: {exc}")
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
