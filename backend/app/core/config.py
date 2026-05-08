import os

from pydantic import BaseModel


def _csv(value: str) -> list[str]:
    return [item.strip().rstrip("/") for item in value.split(",") if item.strip()]


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "VoltStream API")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    cors_origins: list[str] = _csv(
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
    )


settings = Settings()
