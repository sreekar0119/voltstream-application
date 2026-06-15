from __future__ import annotations

from typing import Any

from app.agents.advisor_agent import build_advisor_agent
from app.agents.analyst_agent import build_analyst_agent
from app.agents.device_agent import build_device_agent
from app.agents.prompts import ORCHESTRATOR_INSTRUCTION
from app.agents.tooling import trace_tool_callback
from app.core.config import settings


_AGENT = None
_TOOLS: list[Any] | None = None


def register_orchestrator_tools() -> list[Any]:
    global _TOOLS
    if _TOOLS is not None:
        return _TOOLS

    from google.adk.tools.agent_tool import AgentTool

    _TOOLS = [
        AgentTool(agent=build_analyst_agent(), skip_summarization=False),
        AgentTool(agent=build_advisor_agent(), skip_summarization=False),
        AgentTool(agent=build_device_agent(), skip_summarization=False),
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
        description="Root VoltStream coordinator that delegates to Analyst, Advisor, and Device specialist agents.",
        instruction=ORCHESTRATOR_INSTRUCTION,
        tools=register_orchestrator_tools(),
        output_key="latest_orchestrator_response",
        before_tool_callback=trace_tool_callback("Orchestrator"),
    )
    return _AGENT
