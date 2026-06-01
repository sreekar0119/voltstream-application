from __future__ import annotations

from collections.abc import Callable
from typing import Any, get_type_hints

from app.agents.context import record_trace


def named_tool(name: str, fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    fn.__name__ = name
    fn.__annotations__ = get_type_hints(fn, globalns=fn.__globals__, localns={"Any": Any})
    return fn


def trace_tool_callback(agent_label: str) -> Callable[..., None]:
    def _callback(tool: Any, args: dict[str, Any], **_kwargs: Any) -> None:
        name = getattr(tool, "name", "unknown_tool")
        if name == "get_usage_history":
            message = "[Analyst Agent] Retrieving usage_history..."
        elif name == "calculate_peak_usage":
            message = "[Analyst Agent] Calculating peak consumption..."
        elif name == "summarize_usage_patterns":
            message = "[Analyst Agent] Retrieving usage_history and summarizing energy patterns..."
        elif name == "recommend_energy_saving":
            message = "[Advisor Agent] Generating recommendations..."
        else:
            message = f"[{agent_label}] Calling {name}..."

        record_trace(
            {
                "agent": agent_label,
                "event": "tool_call",
                "message": message,
                "tool": name,
                "args": args,
            }
        )

    return _callback
