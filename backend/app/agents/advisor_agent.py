from __future__ import annotations

from typing import Any

from app.agents.context import require_db
from app.agents.prompts import ADVISOR_INSTRUCTION
from app.agents.tooling import named_tool, trace_tool_callback
from app.core.config import settings
from google.adk.agents import Agent

from app.tools.device_tools import (
    get_active_devices as get_active_devices_tool,
    get_device_status as get_device_status_tool,
)
from app.tools.energy_tools import (
    calculate_total_consumption as calculate_total_consumption_tool,
    recommend_energy_saving as recommend_energy_saving_tool,
)
from app.tools.rag_tool import query_energy_documents as query_energy_documents_tool


_AGENT = None
_TOOLS: list[Any] | None = None


def register_advisor_tools() -> list[Any]:
    global _TOOLS
    if _TOOLS is not None:
        return _TOOLS

    from google.adk.tools import FunctionTool

    def get_active_devices() -> dict[str, Any]:
        """List devices currently switched on before making present-state recommendations."""
        return get_active_devices_tool(require_db())

    def get_device_status(device_name: str) -> dict[str, Any]:
        """Get status, room, category, health, and power usage for a named device."""
        return get_device_status_tool(require_db(), device_name)

    def calculate_total_consumption() -> dict[str, Any]:
        """Calculate current active wattage across all switched-on devices."""
        return calculate_total_consumption_tool(require_db())

    def recommend_energy_saving() -> dict[str, Any]:
        """Find the highest-impact currently active devices to review for savings."""
        return recommend_energy_saving_tool(require_db())

    async def query_energy_documents(query: str) -> dict[str, Any]:
        """Search indexed VoltStream energy PDFs for grounded technical recommendations."""
        return await query_energy_documents_tool(query)

    _TOOLS = [
        FunctionTool(func=named_tool("get_active_devices", get_active_devices)),
        FunctionTool(func=named_tool("get_device_status", get_device_status)),
        FunctionTool(func=named_tool("calculate_total_consumption", calculate_total_consumption)),
        FunctionTool(func=named_tool("recommend_energy_saving", recommend_energy_saving)),
        FunctionTool(func=named_tool("query_energy_documents", query_energy_documents)),
    ]
    return _TOOLS


def build_advisor_agent():
    global _AGENT
    if _AGENT is not None:
        return _AGENT

    #from google.adk.agents import Agent

    _AGENT = Agent(
        name="advisor_agent",
        model=settings.vertex_ai_model or "gemini-2.5-flash",
        description="Specialist agent for VoltStream energy-saving advice and optimization planning.",
        instruction=ADVISOR_INSTRUCTION,
        tools=register_advisor_tools(),
        output_key="latest_energy_advice",
        before_tool_callback=trace_tool_callback("Advisor Agent"),
    )
    return _AGENT
