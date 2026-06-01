from __future__ import annotations

from typing import Any

from app.agents.advisor_agent import build_advisor_agent
from app.agents.analyst_agent import build_analyst_agent
from app.agents.context import require_db
from app.agents.prompts import ORCHESTRATOR_INSTRUCTION
from app.agents.tooling import named_tool, trace_tool_callback
from app.core.config import settings
from app.tools.device_tools import (
    create_device as create_device_tool,
    delete_device as delete_device_tool,
    get_active_devices as get_active_devices_tool,
    get_device_status as get_device_status_tool,
    toggle_device as toggle_device_tool,
)


_AGENT = None
_TOOLS: list[Any] | None = None


def register_orchestrator_tools() -> list[Any]:
    global _TOOLS
    if _TOOLS is not None:
        return _TOOLS

    from google.adk.tools import FunctionTool
    from google.adk.tools.agent_tool import AgentTool

    def toggle_device(device_name: str, state: str) -> dict[str, Any]:
        """Turn a VoltStream device on or off by name when the user requests an operation."""
        if state not in {"on", "off"}:
            return {"ok": False, "message": "State must be 'on' or 'off'.", "changed": False}
        return toggle_device_tool(require_db(), device_name, state)

    def get_device_status(device_name: str) -> dict[str, Any]:
        """Get status, room, category, health, and power usage for a named device."""
        return get_device_status_tool(require_db(), device_name)

    def get_active_devices() -> dict[str, Any]:
        """List devices currently switched on."""
        return get_active_devices_tool(require_db())

    def create_device(name: str, category: str, room: str, power_usage: int) -> dict[str, Any]:
        """Create a smart-home device with room, category, and rated wattage."""
        return create_device_tool(require_db(), name, category, room or "General", int(power_usage), 0)

    def delete_device(device_name: str) -> dict[str, Any]:
        """Delete a smart-home device by name after the target has been identified."""
        return delete_device_tool(require_db(), device_name)

    _TOOLS = [
        AgentTool(agent=build_analyst_agent(), skip_summarization=False),
        AgentTool(agent=build_advisor_agent(), skip_summarization=False),
        FunctionTool(func=named_tool("toggle_device", toggle_device)),
        FunctionTool(func=named_tool("get_device_status", get_device_status)),
        FunctionTool(func=named_tool("get_active_devices", get_active_devices)),
        FunctionTool(func=named_tool("create_device", create_device)),
        FunctionTool(func=named_tool("delete_device", delete_device)),
    ]
    return _TOOLS


def build_orchestrator_agent():
    global _AGENT
    if _AGENT is not None:
        return _AGENT

    from google.adk.agents import Agent

    _AGENT = Agent(
        name="orchestrator_agent",
        model=settings.vertex_ai_model or "gemini-2.5-flash",
        description="Root VoltStream coordinator that delegates to Analyst and Advisor specialist agents.",
        instruction=ORCHESTRATOR_INSTRUCTION,
        tools=register_orchestrator_tools(),
        output_key="latest_orchestrator_response",
        before_tool_callback=trace_tool_callback("Orchestrator"),
    )
    return _AGENT
