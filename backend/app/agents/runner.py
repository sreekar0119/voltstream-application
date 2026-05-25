from __future__ import annotations

import os
from typing import Any, Callable, get_type_hints

from sqlalchemy.orm import Session

from app.agents.prompts import VOLTSTREAM_AGENT_INSTRUCTION
from app.core.config import settings
from app.tools.device_tools import (
    create_device as create_device_tool,
    delete_device as delete_device_tool,
    get_active_devices as get_active_devices_tool,
    get_device_status as get_device_status_tool,
    toggle_device as toggle_device_tool,
)
from app.tools.energy_tools import (
    calculate_total_consumption as calculate_total_consumption_tool,
    recommend_energy_saving as recommend_energy_saving_tool,
)


APP_NAME = "voltstream_agentic_system"
_SESSION_SERVICE = None
_KNOWN_ADK_SESSIONS: set[tuple[str, str]] = set()


def _configure_vertex_environment() -> None:
    if settings.vertex_ai_project:
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.vertex_ai_project)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", settings.vertex_ai_location)
    if settings.google_application_credentials:
        os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(settings.google_application_credentials))


def _named_tool(name: str, fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    fn.__name__ = name
    fn.__annotations__ = get_type_hints(fn, globalns=globals(), localns={"Any": Any})
    return fn


def register_voltstream_tools(db: Session) -> list[Any]:
    try:
        from google.adk.tools import FunctionTool
    except Exception as exc:
        raise RuntimeError("google-adk is not installed or importable. Install backend requirements before using ADK workflows.") from exc

    def toggle_device(device_name: str, state: str) -> dict[str, Any]:
        """Turn a smart-home device on or off by name."""
        if state not in {"on", "off"}:
            return {"ok": False, "message": "State must be 'on' or 'off'.", "changed": False}
        return toggle_device_tool(db, device_name, state)

    def get_device_status(device_name: str) -> dict[str, Any]:
        """Get status, room, category, health, and power usage for a device."""
        return get_device_status_tool(db, device_name)

    def get_active_devices() -> dict[str, Any]:
        """List devices currently switched on."""
        return get_active_devices_tool(db)

    def calculate_total_consumption() -> dict[str, Any]:
        """Calculate total wattage across all currently active devices."""
        return calculate_total_consumption_tool(db)

    def recommend_energy_saving() -> dict[str, Any]:
        """Recommend the highest-impact energy-saving opportunities."""
        return recommend_energy_saving_tool(db)

    def create_device(name: str, category: str, room: str, power_usage: int) -> dict[str, Any]:
        """Create a new smart-home device with room, category, and wattage."""
        return create_device_tool(db, name, category, room or "General", int(power_usage), 0)

    def delete_device(device_name: str) -> dict[str, Any]:
        """Delete a smart-home device by name after identifying the target."""
        return delete_device_tool(db, device_name)

    return [
        FunctionTool(func=_named_tool("toggle_device", toggle_device)),
        FunctionTool(func=_named_tool("get_device_status", get_device_status)),
        FunctionTool(func=_named_tool("get_active_devices", get_active_devices)),
        FunctionTool(func=_named_tool("calculate_total_consumption", calculate_total_consumption)),
        FunctionTool(func=_named_tool("recommend_energy_saving", recommend_energy_saving)),
        FunctionTool(func=_named_tool("create_device", create_device)),
        FunctionTool(func=_named_tool("delete_device", delete_device)),
    ]


def build_voltstream_agent(db: Session):
    try:
        from google.adk.agents import Agent
    except Exception as exc:
        raise RuntimeError("google-adk is not installed or importable. Install backend requirements before using ADK workflows.") from exc

    return Agent(
        name="voltstream_disha",
        model=settings.vertex_ai_model or "gemini-2.5-flash",
        description="VoltStream ADK smart-home energy operator",
        instruction=VOLTSTREAM_AGENT_INSTRUCTION,
        tools=register_voltstream_tools(db),
    )


async def run_adk_agent(db: Session, message: str, user_id: str, session_id: str) -> dict[str, Any]:
    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
    except Exception as exc:
        raise RuntimeError(
            "Google ADK runtime is unavailable. Install backend requirements and restart the server. "
            f"Import error: {exc}"
        ) from exc

    _configure_vertex_environment()

    global _SESSION_SERVICE
    if _SESSION_SERVICE is None:
        _SESSION_SERVICE = InMemorySessionService()
    session_service = _SESSION_SERVICE

    session_key = (user_id, session_id)
    if session_key not in _KNOWN_ADK_SESSIONS:
        try:
            await session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
        except TypeError:
            await session_service.create_session(APP_NAME, user_id, session_id)
        _KNOWN_ADK_SESSIONS.add(session_key)

    runner = Runner(
        agent=build_voltstream_agent(db),
        app_name=APP_NAME,
        session_service=session_service,
    )

    content = types.Content(role="user", parts=[types.Part(text=message)])
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    workflow: list[dict[str, Any]] = [{"step": "ADK_RUNNER", "result": "started"}]
    final_response = ""
    observation: dict[str, Any] | None = None
    tool_name: str | None = None
    changed = False

    async for event in events:
        content_obj = getattr(event, "content", None)
        for part in getattr(content_obj, "parts", []) or []:
            function_call = getattr(part, "function_call", None) or getattr(part, "functionCall", None)
            if function_call:
                tool_name = getattr(function_call, "name", None)
                workflow.append({"step": "TOOL_CALL", "result": tool_name, "args": dict(getattr(function_call, "args", {}) or {})})

            function_response = getattr(part, "function_response", None) or getattr(part, "functionResponse", None)
            if function_response:
                response_payload = getattr(function_response, "response", None)
                if isinstance(response_payload, dict):
                    observation = response_payload
                    changed = changed or bool(response_payload.get("changed"))
                workflow.append({"step": "TOOL_OBSERVATION", "result": response_payload})

        is_final = getattr(event, "is_final_response", None)
        if callable(is_final) and is_final():
            parts = getattr(getattr(event, "content", None), "parts", []) or []
            final_response = "".join(getattr(part, "text", "") or "" for part in parts).strip()
            workflow.append({"step": "FINAL_RESPONSE", "result": final_response})

    if not final_response and observation:
        final_response = str(observation.get("message") or "Done.")
    if not final_response:
        final_response = "I could not complete that workflow."

    return {
        "response": final_response,
        "intent": "agentic_workflow",
        "ai_used": True,
        "changed": changed,
        "tool": tool_name,
        "observation": observation,
        "workflow": workflow,
    }
