from __future__ import annotations

import json
import asyncio
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agents.voltstream_agent import run_voltstream_agent
from app.database import get_db
from app.services.session_manager import session_manager


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: str | None = Field(default=None, max_length=80)


class AgentResponse(BaseModel):
    response: str
    intent: str
    ai_used: bool
    changed: bool = False
    tool: str | None = None
    observation: dict[str, Any] | None = None
    workflow: list[dict[str, Any]] = Field(default_factory=list)
    trace: list[dict[str, Any]] = Field(default_factory=list)
    session_id: str


router = APIRouter(tags=["device-agent"])


@router.post("/agent", response_model=AgentResponse)
async def agent(payload: AgentRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    clean_message = payload.message.strip()
    if not clean_message:
        raise HTTPException(status_code=422, detail="Message is required.")
    session_id = payload.session_id or session_manager.create_session_id()

    return await run_voltstream_agent(
        db=db,
        message=clean_message,
        session_id=session_id,
    )


async def _agent_event_stream(payload: AgentRequest, db: Session) -> AsyncIterator[str]:
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def trace_sink(entry: dict[str, Any]) -> None:
        await queue.put(entry)

    yield f"event: status\ndata: {json.dumps({'state': 'runner_started'})}\n\n"
    task = asyncio.create_task(
        run_voltstream_agent(
            db=db,
            message=payload.message.strip(),
            session_id=payload.session_id,
            trace_sink=trace_sink,
        )
    )

    while not task.done() or not queue.empty():
        try:
            entry = await asyncio.wait_for(queue.get(), timeout=0.15)
        except asyncio.TimeoutError:
            continue
        yield f"event: trace\ndata: {json.dumps(entry, default=str)}\n\n"

    result = await task
    yield f"event: metadata\ndata: {json.dumps({k: v for k, v in result.items() if k != 'response'}, default=str)}\n\n"

    words = result["response"].split(" ")
    for index, word in enumerate(words):
        suffix = " " if index < len(words) - 1 else ""
        yield f"event: token\ndata: {json.dumps({'token': f'{word}{suffix}'})}\n\n"

    yield f"event: done\ndata: {json.dumps({'response': result['response']})}\n\n"


@router.post("/agent/stream")
async def agent_stream(payload: AgentRequest, db: Session = Depends(get_db)) -> StreamingResponse:
    clean_message = payload.message.strip()
    if not clean_message:
        raise HTTPException(status_code=422, detail="Message is required.")

    if not payload.session_id:
        payload.session_id = session_manager.create_session_id()

    return StreamingResponse(
        _agent_event_stream(payload, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
