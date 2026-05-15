from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    mode: str = "chat"
    file_name: str | None = None


class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)


class QAResponse(BaseModel):
    answer: str
    sources: list[str] = []
