import os
from pathlib import Path

from pydantic import BaseModel
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

def _csv(value: str) -> list[str]:
    return [item.strip().rstrip("/") for item in value.split(",") if item.strip()]


def _path(value: str, default: Path) -> Path:
    raw = value.strip()
    if not raw:
        return default
    candidate = Path(raw)
    return candidate if candidate.is_absolute() else BASE_DIR / candidate


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "VoltStream API")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    cors_origins: list[str] = _csv(
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
    )
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    vertex_ai_project: str = os.getenv("VERTEX_AI_PROJECT", os.getenv("GOOGLE_CLOUD_PROJECT", ""))
    vertex_ai_location: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    vertex_ai_model: str = os.getenv("VERTEX_AI_MODEL", "gemini-2.5-flash")
    google_application_credentials: Path | None = (
        _path(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""), BASE_DIR / "secrets" / "service-account.json")
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        else None
    )
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    database_url: Path = _path(os.getenv("DATABASE_URL", ""), BASE_DIR / "voltstream.db")
    documents_dir: Path = _path(os.getenv("DOCUMENTS_DIR", ""), BASE_DIR / "documents")
    chroma_db_dir: Path = _path(os.getenv("CHROMA_DB_DIR", ""), BASE_DIR / "chroma_db")
    rag_collection_name: str = os.getenv("RAG_COLLECTION_NAME", "voltstream_documents")
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "4"))
    rag_chunk_tokens: int = int(os.getenv("RAG_CHUNK_TOKENS", "420"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "60"))


settings = Settings()
