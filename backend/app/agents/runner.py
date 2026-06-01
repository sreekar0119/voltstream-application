from __future__ import annotations

import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy.orm import Session

from app.agents.context import current_db, current_trace
from app.agents.orchestrator_agent import build_orchestrator_agent
from app.core.config import settings


APP_NAME = "voltstream_multi_agent_system"
TraceSink = Callable[[dict[str, Any]], Awaitable[None]]

_SESSION_SERVICE = None
_KNOWN_ADK_SESSIONS: set[tuple[str, str]] = set()
_ADK_WARMED = False

logger = logging.getLogger(__name__)


def _configure_vertex_environment() -> None:
    if settings.vertex_ai_project:
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.vertex_ai_project)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", settings.vertex_ai_location)
    if settings.google_application_credentials:
        os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(settings.google_application_credentials))


def warmup_adk() -> None:
    global _SESSION_SERVICE, _ADK_WARMED
    if _ADK_WARMED:
        return

    try:
        from google.adk.sessions import InMemorySessionService
    except Exception as exc:
        logger.warning("ADK warmup skipped: %s", exc)
        return

    _configure_vertex_environment()
    if _SESSION_SERVICE is None:
        _SESSION_SERVICE = InMemorySessionService()
    build_orchestrator_agent()
    _ADK_WARMED = True


def _agent_label(author: str | None) -> str:
    labels = {
        "orchestrator_agent": "Orchestrator",
        "analyst_agent": "Analyst Agent",
        "advisor_agent": "Advisor Agent",
    }
    return labels.get(author or "", author or "ADK Runner")


def _tool_trace(author: str | None, name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "analyst_agent":
        return {
            "agent": "Orchestrator",
            "event": "delegation",
            "message": "[Orchestrator] Routing request to Analyst Agent...",
            "tool": name,
            "args": args,
        }
    if name == "advisor_agent":
        return {
            "agent": "Orchestrator",
            "event": "delegation",
            "message": "[Orchestrator] Passing analysis to Advisor Agent...",
            "tool": name,
            "args": args,
        }
    if name == "get_usage_history":
        message = "[Analyst Agent] Retrieving usage_history..."
    elif name == "calculate_peak_usage":
        message = "[Analyst Agent] Calculating peak consumption..."
    elif name == "summarize_usage_patterns":
        message = "[Analyst Agent] Retrieving usage_history and summarizing energy patterns..."
    elif name == "recommend_energy_saving":
        message = "[Advisor Agent] Generating recommendations..."
    else:
        message = f"[{_agent_label(author)}] Calling {name}..."

    return {
        "agent": _agent_label(author),
        "event": "tool_call",
        "message": message,
        "tool": name,
        "args": args,
    }


async def _emit(trace: list[dict[str, Any]], entry: dict[str, Any], trace_sink: TraceSink | None) -> None:
    trace.append(entry)
    if trace_sink:
        await trace_sink(entry)


def _parts(event: Any) -> list[Any]:
    content = getattr(event, "content", None)
    return list(getattr(content, "parts", []) or [])


async def _ensure_session(session_service: Any, user_id: str, session_id: str, state: dict[str, Any]) -> None:
    session_key = (user_id, session_id)
    if session_key in _KNOWN_ADK_SESSIONS:
        return

    existing = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    if existing is None:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state=state,
        )
    _KNOWN_ADK_SESSIONS.add(session_key)


async def run_adk_agent(
    db: Session,
    message: str,
    user_id: str,
    session_id: str,
    context: dict[str, Any] | None = None,
    trace_sink: TraceSink | None = None,
) -> dict[str, Any]:
    try:
        from google.adk.runners import Runner
        from google.genai import types
    except Exception as exc:
        raise RuntimeError(
            "Google ADK runtime is unavailable. Install backend requirements and restart the server. "
            f"Import error: {exc}"
        ) from exc

    warmup_adk()

    global _SESSION_SERVICE
    if _SESSION_SERVICE is None:
        raise RuntimeError("ADK session service is not initialized.")

    session_state = {
        "platform": "VoltStream",
        "conversation_context": context or {},
        "handoff_contract": "Orchestrator delegates specialist work through AgentTool and stores specialist outputs in session state.",
    }
    await _ensure_session(_SESSION_SERVICE, user_id, session_id, session_state)

    trace: list[dict[str, Any]] = []
    workflow: list[dict[str, Any]] = []
    await _emit(
        trace,
        {
            "agent": "Orchestrator",
            "event": "runner_start",
            "message": "[Orchestrator] Received request. Starting ADK Runner orchestration...",
        },
        trace_sink,
    )

    db_token = current_db.set(db)
    trace_token = current_trace.set(trace)
    final_response = ""
    observation: dict[str, Any] | None = None
    tool_name: str | None = None
    changed = False

    try:
        runner = Runner(
            agent=build_orchestrator_agent(),
            app_name=APP_NAME,
            session_service=_SESSION_SERVICE,
        )
        content = types.Content(role="user", parts=[types.Part(text=message)])

        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            author = getattr(event, "author", None)
            for part in _parts(event):
                function_call = getattr(part, "function_call", None) or getattr(part, "functionCall", None)
                if function_call:
                    tool_name = getattr(function_call, "name", None) or "unknown_tool"
                    args = dict(getattr(function_call, "args", {}) or {})
                    workflow.append({"step": "TOOL_CALL", "agent": _agent_label(author), "tool": tool_name, "args": args})
                    await _emit(trace, _tool_trace(author, tool_name, args), trace_sink)

                function_response = getattr(part, "function_response", None) or getattr(part, "functionResponse", None)
                if function_response:
                    response_payload = getattr(function_response, "response", None)
                    response_name = getattr(function_response, "name", None) or tool_name or "unknown_tool"
                    if isinstance(response_payload, dict):
                        observation = response_payload
                        changed = changed or bool(response_payload.get("changed"))
                    workflow.append(
                        {
                            "step": "TOOL_OBSERVATION",
                            "agent": _agent_label(author),
                            "tool": response_name,
                            "result": response_payload,
                        }
                    )
                    await _emit(
                        trace,
                        {
                            "agent": _agent_label(author),
                            "event": "tool_observation",
                            "message": f"[{_agent_label(author)}] Received {response_name} result.",
                            "tool": response_name,
                        },
                        trace_sink,
                    )

            is_final = getattr(event, "is_final_response", None)
            if callable(is_final) and is_final():
                parts = _parts(event)
                final_response = "".join(getattr(part, "text", "") or "" for part in parts).strip()
                workflow.append({"step": "FINAL_RESPONSE", "agent": _agent_label(author), "result": final_response})
    finally:
        current_db.reset(db_token)
        current_trace.reset(trace_token)

    if not final_response and observation:
        final_response = str(observation.get("message") or "Done.")
    if not final_response:
        final_response = "I could not complete that ADK multi-agent workflow."

    await _emit(
        trace,
        {
            "agent": "Orchestrator",
            "event": "final_response",
            "message": "[Orchestrator] Synthesizing final response for the user...",
        },
        trace_sink,
    )

    return {
        "response": final_response,
        "intent": "adk_multi_agent_workflow",
        "ai_used": True,
        "changed": changed,
        "tool": tool_name,
        "observation": observation,
        "workflow": workflow,
        "trace": trace,
    }
