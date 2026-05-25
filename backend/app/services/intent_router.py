from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any
from sqlalchemy.orm import Session
from app.tools.device_tools import get_active_devices, get_device_status, toggle_device
from app.tools.energy_tools import calculate_total_consumption


UNKNOWN_COMMAND = "Sorry, I didn't understand that command."


@dataclass(frozen=True)
class IntentPlan:
    intent: str
    tool: str | None = None
    args: dict[str, Any] | None = None
    deterministic: bool = False
    confidence: float = 0.0


def clean_message(message: str) -> str:
    return re.sub(r"\s+", " ", message.lower().strip())


def extract_device_phrase(text: str, verbs: str) -> str:
    pattern = rf"\b(?:{verbs})\b\s+(?:the\s+|a\s+|an\s+|new\s+|smart\s+)*(.+?)\s*(?:using|with|drawing|at|to|please|$)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return ""
    phrase = re.sub(r"\b(on|off|device|appliance|status|state|health|power|usage|watts?)\b", "", match.group(1), flags=re.IGNORECASE)
    return " ".join(phrase.split()).strip()


def route_local_intent(message: str) -> IntentPlan:
    text = clean_message(message)
    if not text:
        return IntentPlan(intent="unknown")

    if re.search(r"\b(turn on|switch on|activate|enable|start|power on)\b", text):
        device = extract_device_phrase(text, "turn on|switch on|activate|enable|start|power on")
        if device:
            return IntentPlan(
                intent="toggle_device",
                tool="toggle_device",
                args={"device_name": device, "state": "on"},
                deterministic=True,
                confidence=0.96,
            )

    if re.search(r"\b(turn off|switch off|deactivate|disable|stop|power off)\b", text):
        device = extract_device_phrase(text, "turn off|switch off|deactivate|disable|stop|power off")
        if device:
            return IntentPlan(
                intent="toggle_device",
                tool="toggle_device",
                args={"device_name": device, "state": "off"},
                deterministic=True,
                confidence=0.96,
            )

    if re.search(r"\b(show|list|get)\b.*\b(active|online|running)\b.*\bdevices?\b", text) or "active devices" in text:
        return IntentPlan(
            intent="active_devices",
            tool="get_active_devices",
            args={},
            deterministic=True,
            confidence=0.95,
        )

    if re.search(r"\b(total|current|active)\b.*\b(consumption|load|usage|draw)\b", text):
        return IntentPlan(
            intent="consumption",
            tool="calculate_total_consumption",
            args={},
            deterministic=True,
            confidence=0.9,
        )

    if re.search(r"\b(status|state|health|power usage|power draw|watts?)\b", text):
        device = extract_device_phrase(text, "status of|state of|health of|power usage of|watts for|check|show|get")
        if not device:
            device = re.sub(
                r"\b(what is|what's|show|get|check|the|status|state|health|power usage|power draw|watts|wattage|of|for|please)\b",
                "",
                text,
                flags=re.IGNORECASE,
            )
            device = " ".join(device.split()).strip()
        if device and device not in {"its", "it"}:
            return IntentPlan(
                intent="device_status",
                tool="get_device_status",
                args={"device_name": device},
                deterministic=True,
                confidence=0.88,
            )

    return IntentPlan(intent="agentic_workflow", deterministic=False, confidence=0.35)


def execute_local_tool(db: Session, plan: IntentPlan) -> dict[str, Any]:
    args = plan.args or {}
    try:
        if plan.tool == "toggle_device":
            return toggle_device(db, args["device_name"], args["state"])
        if plan.tool == "get_device_status":
            return get_device_status(db, args["device_name"])
        if plan.tool == "get_active_devices":
            return get_active_devices(db)
        if plan.tool == "calculate_total_consumption":
            return calculate_total_consumption(db)
    except Exception as exc:
        return {"ok": False, "message": f"Tool execution failed: {exc}", "changed": False}
    return {"ok": False, "message": UNKNOWN_COMMAND, "changed": False}
