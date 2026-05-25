from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.runner import run_adk_agent
from app.agents.session_manager import session_manager
from app.services.intent_router import UNKNOWN_COMMAND, execute_local_tool, route_local_intent


def _workflow_entry(step: str, result: Any, **extra: Any) -> dict[str, Any]:
    payload = {"step": step, "result": result}
    payload.update(extra)
    return payload


async def run_voltstream_agent(
    db: Session,
    message: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    session = session_manager.get_or_create(session_id=session_id)
    resolved_message = session_manager.resolve_references(message, session)
    plan = route_local_intent(resolved_message)
    workflow = [
        _workflow_entry("INPUT", message, channel="text"),
        _workflow_entry("LOCAL_INTENT_ROUTER", plan.intent, confidence=plan.confidence),
    ]

    if plan.deterministic and plan.tool:
        observation = execute_local_tool(db, plan)
        response = observation.get("message") or UNKNOWN_COMMAND
        workflow.extend(
            [
                _workflow_entry("DIRECT_TOOL_EXECUTION", plan.tool),
                _workflow_entry("OBSERVATION", observation),
                _workflow_entry("RESPOND", response),
            ]
        )
        session.remember(message, response, observation)
        return {
            "response": response,
            "intent": plan.intent,
            "tool": plan.tool,
            "ai_used": False,
            "changed": bool(observation.get("changed")),
            "observation": observation,
            "workflow": workflow,
            "session_id": session.session_id,
        }

    workflow.append(_workflow_entry("ROUTE_TO_ADK_RUNNER", "complex_or_ambiguous"))
    try:
        adk_result = await run_adk_agent(
            db=db,
            message=resolved_message,
            user_id=session.user_id,
            session_id=session.session_id,
        )
        adk_result["workflow"] = workflow + adk_result.get("workflow", [])
        adk_result["session_id"] = session.session_id
        session.remember(message, adk_result["response"], adk_result.get("observation"))
        return adk_result
    except Exception as exc:
        response = f"I could not start the ADK reasoning workflow: {exc}"
        workflow.append(_workflow_entry("ADK_ERROR", str(exc)))
        return {
            "response": response,
            "intent": "agentic_workflow",
            "ai_used": True,
            "changed": False,
            "tool": None,
            "observation": None,
            "workflow": workflow,
            "session_id": session.session_id,
        }
