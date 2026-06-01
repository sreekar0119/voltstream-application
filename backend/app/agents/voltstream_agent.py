from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.runner import TraceSink, run_adk_agent
from app.services.session_manager import session_manager


def _recent_context(session: Any) -> dict[str, Any]:
    return {
        "last_device_name": session.last_device_name,
        "recent_turns": session.recent_turns[-6:],
    }


async def run_voltstream_agent(
    db: Session,
    message: str,
    session_id: str | None = None,
    trace_sink: TraceSink | None = None,
) -> dict[str, Any]:
    session = session_manager.get_or_create(session_id=session_id)
    resolved_message = session_manager.resolve_references(message, session)

    try:
        adk_result = await run_adk_agent(
            db=db,
            message=resolved_message,
            user_id=session.user_id,
            session_id=session.session_id,
            context=_recent_context(session),
            trace_sink=trace_sink,
        )
        adk_result["session_id"] = session.session_id
        session.remember(message, adk_result["response"], adk_result.get("observation"))
        return adk_result
    except Exception as exc:
        response = f"I could not start the ADK multi-agent workflow: {exc}"
        return {
            "response": response,
            "intent": "adk_multi_agent_workflow",
            "ai_used": True,
            "changed": False,
            "tool": None,
            "observation": None,
            "workflow": [{"step": "ADK_ERROR", "result": str(exc)}],
            "trace": [
                {
                    "agent": "ADK Runner",
                    "event": "error",
                    "message": f"[ADK Runner] {exc}",
                }
            ],
            "session_id": session.session_id,
        }
