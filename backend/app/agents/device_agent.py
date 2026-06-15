from __future__ import annotations

from typing import Any

from app.agents.context import require_db
from app.agents.prompts import DEVICE_INSTRUCTION
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


def register_device_tools() -> list[Any]:
    global _TOOLS
    if _TOOLS is not None:
        return _TOOLS

    from google.adk.tools import FunctionTool

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
        FunctionTool(func=named_tool("toggle_device", toggle_device)),
        FunctionTool(func=named_tool("get_device_status", get_device_status)),
        FunctionTool(func=named_tool("get_active_devices", get_active_devices)),
        FunctionTool(func=named_tool("create_device", create_device)),
        FunctionTool(func=named_tool("delete_device", delete_device)),
    ]
    return _TOOLS


def build_device_agent():
    global _AGENT
    if _AGENT is not None:
        return _AGENT

    from google.adk.agents import Agent

    _AGENT = Agent(
        name="device_agent",
        model=settings.vertex_ai_model or "gemini-2.5-flash",
        description="Specialist agent for VoltStream smart-home device status and operations.",
        instruction=DEVICE_INSTRUCTION,
        tools=register_device_tools(),
        output_key="latest_device_operation",
        before_tool_callback=trace_tool_callback("Device Agent"),
    )
    return _AGENT
