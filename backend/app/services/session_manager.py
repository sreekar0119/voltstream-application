from __future__ import annotations

from dataclasses import dataclass, field
import re
from time import time
from typing import Any
from uuid import uuid4


@dataclass
class LightweightSession:
    session_id: str
    user_id: str
    last_device_name: str | None = None
    recent_turns: list[dict[str, Any]] = field(default_factory=list)
    updated_at: float = field(default_factory=time)

    def remember(self, message: str, response: str, observation: dict[str, Any] | None = None) -> None:
        device = (observation or {}).get("device") or {}
        if isinstance(device, dict) and device.get("name"):
            self.last_device_name = str(device["name"])
        self.recent_turns.append({"user": message, "assistant": response})
        self.recent_turns = self.recent_turns[-6:]
        self.updated_at = time()


class VoltStreamSessionManager:
    def __init__(self) -> None:
        self._sessions: dict[tuple[str, str], LightweightSession] = {}

    def get_or_create(self, user_id: str = "voltstream-user", session_id: str | None = None) -> LightweightSession:
        sid = session_id or self.create_session_id()
        key = (user_id, sid)
        if key not in self._sessions:
            self._sessions[key] = LightweightSession(session_id=sid, user_id=user_id)
        return self._sessions[key]

    def create_session_id(self) -> str:
        return f"vs-{uuid4().hex[:12]}"

    def resolve_references(self, message: str, session: LightweightSession) -> str:
        if not session.last_device_name:
            return message
        lowered = message.lower()
        if re.search(r"\b(it|its|that device|that appliance)\b", lowered):
            return re.sub(
                r"\b(its|it|that device|that appliance)\b",
                session.last_device_name,
                message,
                flags=re.IGNORECASE,
            )
        return message


session_manager = VoltStreamSessionManager()
