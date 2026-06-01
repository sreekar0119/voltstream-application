from __future__ import annotations

from typing import Any, Literal

from app.agents.context import require_db
from app.agents.prompts import ANALYST_INSTRUCTION
from app.agents.tooling import named_tool, trace_tool_callback
from app.core.config import settings
from app.tools.analytics_tools import (
    calculate_peak_usage as calculate_peak_usage_tool,
    get_usage_history as get_usage_history_tool,
    summarize_usage_patterns as summarize_usage_patterns_tool,
)
from app.tools.device_tools import get_active_devices as get_active_devices_tool
from app.tools.energy_tools import calculate_total_consumption as calculate_total_consumption_tool


_AGENT = None
_TOOLS: list[Any] | None = None


def register_analyst_tools() -> list[Any]:
    global _TOOLS
    if _TOOLS is not None:
        return _TOOLS

    from google.adk.tools import FunctionTool

    def get_usage_history(period: Literal["24h", "7d", "30d", "all"] = "7d") -> dict[str, Any]:
        """Retrieve per-device energy usage history from VoltStream's usage_history table."""
        return get_usage_history_tool(require_db(), period)

    def calculate_peak_usage(period: Literal["24h", "7d", "30d", "all"] = "7d") -> dict[str, Any]:
        """Calculate the highest usage window and top contributing device for a period."""
        return calculate_peak_usage_tool(require_db(), period)

    def summarize_usage_patterns(period: Literal["24h", "7d", "30d", "all"] = "7d") -> dict[str, Any]:
        """Summarize totals, peak windows, and top device patterns for energy usage."""
        return summarize_usage_patterns_tool(require_db(), period)

    def get_active_devices() -> dict[str, Any]:
        """List devices currently switched on when present-state context is useful for analysis."""
        return get_active_devices_tool(require_db())

    def calculate_total_consumption() -> dict[str, Any]:
        """Calculate the current active wattage across devices that are switched on."""
        return calculate_total_consumption_tool(require_db())

    _TOOLS = [
        FunctionTool(func=named_tool("get_usage_history", get_usage_history)),
        FunctionTool(func=named_tool("calculate_peak_usage", calculate_peak_usage)),
        FunctionTool(func=named_tool("summarize_usage_patterns", summarize_usage_patterns)),
        FunctionTool(func=named_tool("get_active_devices", get_active_devices)),
        FunctionTool(func=named_tool("calculate_total_consumption", calculate_total_consumption)),
    ]
    return _TOOLS


def build_analyst_agent():
    global _AGENT
    if _AGENT is not None:
        return _AGENT

    from google.adk.agents import Agent

    _AGENT = Agent(
        name="analyst_agent",
        model=settings.vertex_ai_model or "gemini-2.5-flash",
        description="Specialist agent for VoltStream usage history, trend, and peak-load analysis.",
        instruction=ANALYST_INSTRUCTION,
        tools=register_analyst_tools(),
        output_key="latest_usage_analysis",
        before_tool_callback=trace_tool_callback("Analyst Agent"),
    )
    return _AGENT
