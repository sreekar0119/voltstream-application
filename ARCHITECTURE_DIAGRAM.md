# 🏗️ VoltStream ADK Agent Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          🌐 CLIENT LAYER                                    │
│                     React Frontend (Browser)                                │
│              User sends: "Turn off the Air Conditioning"                    │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ HTTP POST Request        │
                    │ /api/v1/agent/stream     │
                    │ {message, session_id}    │
                    └────────────┬─────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────┐
        │   ⚡ FASTAPI ROUTER LAYER                 │
        ├────────────────────────────────────────────┤
        │ 1. Request Validator (AgentRequest)       │
        │ 2. Session Manager (get_or_create)        │
        │ 3. Route to Agent Orchestrator            │
        └────────────────────┬───────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────────────────────┐
        │          🤖 AGENT ORCHESTRATION LAYER                         │
        ├────────────────────────────────────────────────────────────────┤
        │                                                                │
        │ voltstream_agent.py: run_voltstream_agent()                  │
        │ ├─ Get/Create Session                                        │
        │ ├─ Resolve Pronouns (it → AC)                               │
        │ └─ Route Intent                                             │
        │                                                                │
        └────────────────────┬─────────────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
    ┌──────────────────────┐  ┌─────────────────────────┐
    │ LOCAL PATH (FAST)    │  │ ADK AGENT PATH (SMART)  │
    │ ~100ms               │  │ ~1-3 seconds            │
    │                      │  │                         │
    │ route_local_intent() │  │ run_adk_agent()        │
    │ ↓                    │  │ ↓                       │
    │ Deterministic?       │  │ Google ADK Agent       │
    │ YES                  │  │ (gemini-1.5-flash)     │
    │ ↓                    │  │ ├─ Read instruction    │
    │ execute_local_tool() │  │ ├─ Analyze message    │
    │                      │  │ ├─ Plan response      │
    │ Result:              │  │ └─ Select tool        │
    │ {ok, message}        │  │                        │
    │                      │  └──────────┬─────────────┘
    └────────────┬─────────┘             │
                 │                       ▼
                 │             ┌──────────────────────────┐
                 │             │ ADK TOOL SELECTOR        │
                 │             │                          │
                 │             │ Which tool to call?      │
                 │             └──────────┬───────────────┘
                 │                        │
                 │          ┌─────────────┴─────────────┐
                 │          │                           │
                 │          ▼                           ▼
                 │    toggle_device?            get_device_status?
                 │    create_device?            recommend_energy?
                 │    delete_device?            ... (7 total tools)
                 │          │                           │
                 └──────────┼───────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────────────┐
            │    💾 DATABASE INTERACTION LAYER      │
            ├───────────────────────────────────────┤
            │ device_tools.py (Tool Execution)     │
            │ ├─ Fuzzy Match (0.7 threshold)      │
            │ ├─ Word Boundary Check              │
            │ ├─ SQLAlchemy ORM Query             │
            │ ├─ DeviceModel Update/Query         │
            │ └─ Return Observation               │
            │     {ok, message, changed}          │
            └───────────────┬───────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────────────┐
            │  📋 RESPONSE PIPELINE                │
            ├───────────────────────────────────────┤
            │ 1. Build Workflow Log (all steps)   │
            │    [{step: "PLAN", result: "..."}] │
            │                                     │
            │ 2. Format AgentResponse             │
            │    {response, intent, ai_used...}  │
            │                                     │
            │ 3. Stream SSE Events to Client      │
            │    ├─ event: metadata               │
            │    ├─ event: token                  │
            │    ├─ event: token                  │
            │    └─ event: done                   │
            └───────────────┬───────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────────────┐
            │  📤 FRONTEND STATE UPDATE             │
            ├───────────────────────────────────────┤
            │ • Accumulate tokens → display       │
            │ • Update aiUsed badge               │
            │ • Persist session_id                │
            │ • Dispatch devices-updated event    │
            │ • Show "Air Conditioning turned off"│
            └───────────────────────────────────────┘
```

---

## 📊 Agent Loop: Step-by-Step Execution

### User: "Turn off the Air Conditioning"

```
STEP 1: PLAN
  Input: "Turn off the Air Conditioning"
  Intent Router analyzes: contains "turn off" + device name
  Decision: Not deterministic (needs fuzzy matching + confirmation)
  Action: Route to ADK Agent
  ✓ Confidence: 0.85

STEP 2: SELECT TOOL
  Agent (Gemini) reasons: "User wants toggle_device"
  Devices searched: "Air Conditioning" → finds AC device (fuzzy match 0.95)
  Selected Tool: toggle_device
  Parameters: {device_name: "AC", state: "off"}

STEP 3: EXECUTE
  Tool: toggle_device(db, "AC", "off")
  ├─ Find device in DB (FuzzyMatcher)
  ├─ Check current state: "on"
  ├─ Update: device.status = "off"
  ├─ Commit to database
  └─ Return observation

STEP 4: OBSERVE
  Result: {
    ok: true,
    changed: true,
    message: "Air Conditioning turned off",
    device: {
      id: 5,
      name: "Air Conditioning",
      status: "off",
      power_usage: 2500
    }
  }

STEP 5: RESPOND
  Agent crafts response: "Air Conditioning has been turned off"
  Format: AgentResponse {
    response: "Air Conditioning has been turned off",
    intent: "agentic_workflow",
    ai_used: true,
    changed: true,
    tool: "toggle_device",
    observation: {...},
    workflow: [step1, step2, step3, step4, step5]
  }

STEP 6: STREAM TO CLIENT
  Event 1: metadata {ai_used: true, session_id: "vs-xxx"}
  Event 2: token "Air"
  Event 3: token "Conditioning"
  Event 4: token "has"
  Event 5: token "been"
  Event 6: token "turned"
  Event 7: token "off"
  Event 8: done {response: "..."}

⏱️ Total Time: 1.2 seconds
🔧 Tools Used: 1 (toggle_device)
✅ Success: Device state updated in DB
```

---

## 🔧 Tool System: 7 Registered Tools

```python
# All tools registered as FunctionTool with ADK

1. toggle_device(device_name: str, state: str)
   └─ Turns device on/off

2. get_device_status(device_name: str)
   └─ Returns device details

3. get_active_devices()
   └─ Lists all active devices

4. calculate_total_consumption()
   └─ Total power draw

5. recommend_energy_saving()
   └─ Energy optimization advice

6. create_device(name: str, category: str, room: str, power_usage: int)
   └─ Add new device

7. delete_device(device_name: str)
   └─ Remove device
```

---

## 🔄 Request/Response Flow

### Request (Client → Server)
```json
{
  "message": "Turn off the Air Conditioning",
  "session_id": "vs-a1b2c3d4e5f6"
}
```

### Response (Streaming)
```
event: metadata
data: {"intent": "agentic_workflow", "ai_used": true, "session_id": "vs-xxx", "changed": true}

event: token
data: {"token": "Air "}

event: token
data: {"token": "Conditioning "}

event: token
data: {"token": "has "}

event: token
data: {"token": "been "}

event: token
data: {"token": "turned "}

event: token
data: {"token": "off"}

event: done
data: {"response": "Air Conditioning has been turned off"}
```

---

## 📁 Key Files in This Architecture

| File | Purpose | Key Function |
|------|---------|--------------|
| `backend/app/routers/agent.py` | HTTP endpoints | `@router.post("/agent/stream")` |
| `backend/app/agents/voltstream_agent.py` | Agent orchestrator | `run_voltstream_agent()` |
| `backend/app/agents/runner.py` | ADK executor | `run_adk_agent()` |
| `backend/app/services/intent_router.py` | Intent detection | `route_local_intent()` |
| `backend/app/agents/session_manager.py` | Session management | `get_or_create()` |
| `backend/app/agents/prompts.py` | Agent instruction | `VOLTSTREAM_AGENT_INSTRUCTION` |
| `backend/app/tools/device_tools.py` | Tool implementation | `toggle_device()` |

---

## ⚡ Performance Characteristics

| Scenario | Latency | Path | Details |
|----------|---------|------|---------|
| Simple toggle (local) | ~100ms | Local | Pattern match + execute |
| Complex reasoning | 1-3 sec | ADK | Gemini reasoning + tool call |
| Multi-turn dialog | Per turn | ADK | Session memory resolves pronouns |
| Streaming overhead | ~10ms | Both | SSE event formatting |

---

## 🎯 Design Principles

### 1. **Hybrid Execution**
- Fast path: Deterministic commands (toggle, status)
- Smart path: Complex/ambiguous requests (ADK reasoning)

### 2. **Tool-Driven Agent**
- All device operations exposed as tools
- ADK learns which tool to call from context
- No hardcoded decision logic

### 3. **Session-Aware**
- Remembers last device accessed
- Resolves pronouns automatically ("it" → device name)
- Maintains conversation context

### 4. **Observable Execution**
- Complete workflow trace logged
- Every step documented
- Debugging information included

### 5. **Streaming First**
- Tokens streamed to client in real-time
- Better UX (incremental display)
- Metadata available immediately

---

## ✅ Requirements Fulfillment

| Week 4 Requirement | Status | Evidence |
|-------------------|--------|----------|
| Understand agent loop | ✅ | All 5 steps (plan→select→execute→observe→respond) implemented |
| Setup ADK & credentials | ✅ | runner.py configures Vertex environment |
| Tool calling in Python | ✅ | 7 FunctionTool objects registered |
| Structured output | ✅ | AgentResponse Pydantic model |
| Custom tools (2+) | ✅ | 7 tools built (exceeds requirement) |
| /api/v1/agent endpoint | ✅ | POST + streaming variants |
| Test: "Turn off AC" | ✅ | Complete flow implemented |
| Architecture diagram | ✅ | This document + Mermaid diagram |
| GitHub + explanation | ✅ | Code in repo + workflow documented |

---

**Status: Architecture Complete & Documented ✨**
