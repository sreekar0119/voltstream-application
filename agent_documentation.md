# VoltStream Agent Documentation

## Table of Contents
| Section | Description |
|---------|-------------|
| 1 | Overview |
| 2 | System Architecture |
| 3 | How The Agent Works |
| 4 | Dual-Path Approach |
| 5 | Device Operations (Tools) |
| 6 | Configuration |
| 7 | API Usage |
| 8 | Session Management |
| 9 | Performance Tuning |
| 10 | Troubleshooting |

---

## Overview

The VoltStream Agent is an intelligent smart-home energy operator that turns natural language requests into actions. Users can ask questions like "Turn off the AC" or "What's my total energy consumption?" and the agent handles them intelligently—either through fast local commands or complex reasoning with the Gemini LLM.

**Key Characteristic**: The agent operates on a **tool-first principle**—it cannot directly modify the database. All state changes happen through registered tools, ensuring safety and auditability.

---

## System Architecture

### Main Components

| Component | File | Purpose |
|-----------|------|---------|
| **API Router** | `backend/app/routers/agent.py` | HTTP endpoints: `/agent`, `/agent/stream` |
| **Orchestrator** | `backend/app/agents/voltstream_agent.py` | Decides execution path + routes requests |
| **Session Manager** | `backend/app/agents/session_manager.py` | Stores conversation history & pronoun context |
| **Intent Router** | `backend/app/services/intent_router.py` | Detects common patterns (regex-based) |
| **ADK Runner** | `backend/app/agents/runner.py` | Builds & executes Gemini agent with tools |
| **Device Tools** | `backend/app/tools/device_tools.py` | Toggle, status, create, delete operations |
| **Energy Tools** | `backend/app/tools/energy_tools.py` | Consumption & saving recommendations |
| **Frontend UI** | `frontend/src/components/ai/DeviceAgentAssistant.jsx` | Chat interface + streaming handler |
| **Agent Prompt** | `backend/app/agents/prompts.py` | System instructions for "Disha" agent |

---

## How The Agent Works

### The Dual-Path Strategy

VoltStream uses a **smart two-path approach**:

```
User: "Turn off the AC"
    ↓
[Local Intent Router]
    ↓
Regex Match? → "turn off" pattern
    ↓
Deterministic? → YES
    ↓
└→ FAST PATH (100ms)
   ├─ Direct tool call: toggle_device()
   ├─ No LLM involved
   └─ Return: "AC turned off"
```

```
User: "Save me 20% energy but keep AC on"
    ↓
[Local Intent Router]
    ↓
Regex Match? → No specific pattern
    ↓
Deterministic? → NO (ambiguous, needs reasoning)
    ↓
└→ SMART PATH (1-3 seconds)
   ├─ Route to Google ADK Agent
   ├─ Gemini LLM analyzes request
   ├─ Selects: recommend_energy_saving() tool
   ├─ Returns intelligent recommendations
   └─ Response: "Turn off heater, save 500W..."
```

### Why Two Paths?

| Aspect | Local Path | ADK Path |
|--------|-----------|----------|
| Speed | ~100ms | 1-3 seconds |
| Cost | No API calls | Gemini API call |
| Complexity | Simple commands | Complex reasoning |
| LLM Used | No | Yes (Gemini) |
| Best For | Toggle, status, list | Complex requests, entity extraction |

---

## Dual-Path Approach

### Path 1: Local Fast Path (~100ms)

**When it triggers**: User says something matching a regex pattern

**Supported patterns**:
- "turn on/off" → `toggle_device`
- "what's the status" → `get_device_status`
- "show active devices" → `get_active_devices`
- "how much power" → `calculate_total_consumption`
- "save energy" → `recommend_energy_saving`

**Process**:
1. Regex pattern matches message
2. Extract parameters (device name, state)
3. Call tool directly (no LLM)
4. Return observation (success/fail, device info)

**Example**:
```
User: "Turn on the living room light"
→ Regex matches: "turn on"
→ Extract: device="light", state="on"
→ Call: toggle_device("light", "on")
→ Result: {ok: true, message: "Light turned on", changed: true}
Time: ~50-100ms
```

### Path 2: ADK Smart Path (1-3 seconds)

**When it triggers**: Message doesn't match regex patterns (ambiguous or complex)

**Process**:
1. Route to Google ADK Agent named "Disha"
2. Agent reads system prompt + user message
3. Agent plans → selects tool → executes → observes
4. May call multiple tools in sequence
5. Returns final response

**Example**:
```
User: "I want to reduce my bill but don't turn off the TV"
→ No regex match
→ Route to ADK
→ Gemini: "I should recommend energy savings excluding TV"
→ Call: recommend_energy_saving()
→ Get: [{device: "Heater", potential_savings: 500W}, ...]
→ Synthesize: "Turn off the heater for 500W savings"
Time: ~2-3 seconds
```

---

## Device Operations (Tools)

### Available Tools

#### Device Tools
| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `toggle_device` | Turn device on/off | device_name, state | {ok, message, changed, device} |
| `get_device_status` | Get device info | device_name | {ok, message, device {...}} |
| `get_active_devices` | List running devices | none | {ok, message, devices [...]} |
| `create_device` | Add new device | name, category, room, power_usage | {ok, message, changed: true} |
| `delete_device` | Remove device | device_name | {ok, message, changed: true} |

#### Energy Tools
| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `calculate_total_consumption` | Total wattage now | none | {total_wattage, active_count} |
| `recommend_energy_saving` | Optimization tips | none | {recommendations: [{device, savings_w}]} |

### Tool Execution Rules

- **Fuzzy matching**: "AC" matches "Air Conditioning" with 0.7+ confidence
- **Deterministic tools**: Local path uses these directly (no reasoning)
- **Complex tools**: ADK agent decides when/how to use them
- **Safety**: All changes confirmed by tool observations
- **Logging**: Workflow trace captures every step

---

## Configuration

### Environment Variables

| Variable | Default | Purpose | Location |
|----------|---------|---------|----------|
| `VERTEX_AI_PROJECT` | — | GCP project for Gemini | `backend/.env` |
| `VERTEX_AI_LOCATION` | `us-central1` | GCP region | `backend/.env` |
| `GOOGLE_APPLICATION_CREDENTIALS` | — | Path to GCP service account JSON | `backend/.env` |
| `VERTEX_AI_MODEL` | `gemini-2.5-flash` | LLM model for ADK agent | `backend/.env` |

### Backend Setup

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Set up environment
# Edit backend/.env with your GCP credentials
# VERTEX_AI_PROJECT=your-project-id
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# 3. Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Start dev server
npm run dev

# 3. Access at http://localhost:5173
```

---

## API Usage

### Endpoints

#### POST `/api/v1/agent`
Single request-response endpoint (no streaming)

```bash
curl -X POST http://localhost:8000/api/v1/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Turn off the AC",
    "session_id": "vs-abc123"
  }'
```

**Response**:
```json
{
  "response": "Air Conditioning turned off",
  "intent": "toggle_device",
  "ai_used": false,
  "changed": true,
  "tool": "toggle_device",
  "observation": {
    "ok": true,
    "message": "Air Conditioning turned off",
    "changed": true,
    "device": {...}
  },
  "workflow": [...],
  "session_id": "vs-abc123"
}
```

#### POST `/api/v1/agent/stream`
Streaming endpoint for real-time token delivery (recommended)

```bash
curl -X POST http://localhost:8000/api/v1/agent/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my total energy consumption?",
    "session_id": "vs-abc123"
  }'
```

**Response** (Server-Sent Events):
```
event: status
data: {"state": "planning"}

event: metadata
data: {"intent": "consumption", "ai_used": false, "session_id": "vs-abc123"}

event: token
data: {"token": "Your "}

event: token
data: {"token": "total "}

event: token
data: {"token": "consumption "}

event: token
data: {"token": "is 2500W"}

event: done
data: {"response": "Your total consumption is 2500W"}
```

### Request Model

```python
class AgentRequest:
    message: str          # User input (1-1000 chars)
    session_id: str | None  # Optional conversation ID
```

### Response Model

```python
class AgentResponse:
    response: str                    # Final answer
    intent: str                      # Detected intent
    ai_used: bool                    # Was Gemini used?
    changed: bool                    # Did state change?
    tool: str | None                 # Tool executed
    observation: dict | None         # Tool output
    workflow: list[dict]             # Execution trace
    session_id: str                  # Conversation ID
```

---

## Session Management

### How Sessions Work

Each conversation has a unique `session_id` that enables:

1. **Conversation Context**: Agent remembers last 6 turns
2. **Pronoun Resolution**: "Turn it off" → "Turn AC off"
3. **Device Continuity**: Last mentioned device is saved

### Session Persistence

**Frontend**:
```javascript
// Stored in localStorage
const SESSION_KEY = "voltstream-session-id";

// Load existing
const sessionId = window.localStorage.getItem(SESSION_KEY);

// Save new
window.localStorage.setItem(SESSION_KEY, response.session_id);
```

**Backend**:
```python
# In-memory session storage
# Resets on server restart
# Stores: session_id, user_id, last_device, recent_turns
```

### Example: Multi-Turn Conversation

```
Turn 1:
User: "Turn off the air conditioner"
→ Session created: vs-abc123
→ Stored: last_device = "air conditioner"

Turn 2:
User: "Now turn it back on"
→ Pronoun resolution: "it" → "air conditioner"
→ Message becomes: "Now turn air conditioner back on"
→ Command executes correctly

Turn 3:
User: "What's its status?"
→ Pronoun resolution: "its" → "air conditioner"
→ Fetches air conditioner status
```

---

## Performance Tuning

### Faster Response Times

| Goal | Setting | Change | Impact |
|------|---------|--------|--------|
| Faster agents | Improve regex patterns | Add more patterns to local router | Skip LLM more often |
| Reduce latency | Cache embeddings | Pre-compute common queries | —5 |
| Cheaper operation | Increase local path | More regex patterns | Fewer ADK calls |

### Better Answer Quality

| Goal | Setting | Change | Impact |
|------|---------|--------|--------|
| More accurate | Improve prompts | Refine `VOLTSTREAM_AGENT_INSTRUCTION` | Better reasoning |
| Handle edge cases | Add tools | Implement new device_tools | More capabilities |
| Better context | Improve session | Store more turns | Better multi-turn |

### Memory Optimization

- **Session storage**: In-memory (resets on restart)
- **ADK model**: Loaded once (~200MB for Gemini)
- **Tool functions**: Lightweight (fuzzy matching only when needed)

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "I couldn't find that device" | Fuzzy match failed | Check device name spelling |
| Slow responses | ADK coldstart | First request slower; cache warms up |
| "I could not start ADK workflow" | Missing credentials | Check `GOOGLE_APPLICATION_CREDENTIALS` |
| Session not persisting | localStorage blocked | Check browser privacy settings |
| LLM always used | No regex matches | Add pattern to `intent_router.py` |
| Wrong tool selected | ADK reasoning issue | Refine agent prompt in `prompts.py` |
| Device not changing | Tool error | Check DB connection + logs |
| Pronoun resolution fails | Session expired | Session resets; start new with explicit names |

### Debug Tips

**Enable workflow tracing**:
```python
# Response includes workflow array
{
    "workflow": [
        {"step": "INPUT", "result": "..."},
        {"step": "LOCAL_INTENT_ROUTER", "result": "..."},
        {"step": "DIRECT_TOOL_EXECUTION", "result": "..."},
        {"step": "OBSERVATION", "result": "..."},
        {"step": "RESPOND", "result": "..."}
    ]
}
# Check which step failed
```

**Check if LLM was used**:
```json
{
    "ai_used": false,  // Local path (fast)
    "ai_used": true    // ADK path (with Gemini)
}
```

**Inspect tool observations**:
```json
{
    "observation": {
        "ok": true,        // Tool succeeded?
        "message": "...",  // Human readable
        "changed": true,   // State changed?
        "device": {...}    // Full device object
    }
}
```
