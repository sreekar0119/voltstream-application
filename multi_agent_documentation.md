# VoltStream Multi-Agent Documentation

## Table of Contents
| Section | Description |
|---------|-------------|
| 1 | Overview |
| 2 | System Architecture |
| 3 | How The Multi-Agent System Works |
| 4 | Agent Routing Approach |
| 5 | Agent Responsibilities And Tools |
| 6 | Configuration |
| 7 | API Usage |
| 8 | Session Management |
| 9 | Performance Tuning |
| 10 | Troubleshooting |

---

## Overview

The VoltStream Multi-Agent System is a smart-home energy assistant built with Google ADK. It converts natural language requests into grounded device operations, usage analysis, and energy-saving recommendations.

Instead of relying on one general-purpose agent for every task, VoltStream uses a coordinator-specialist design:

- The Orchestrator Agent receives every user request.
- The Analyst Agent handles usage history, trends, peak windows, and consumption analysis.
- The Advisor Agent handles optimization advice, saving recommendations, and next-action planning.
- Direct device tools are used by the Orchestrator for operational requests such as turning devices on or off.

**Key Characteristic**: The system follows a tool-first principle. Agents do not directly mutate the database or invent device state. All device changes, status checks, analytics, and recommendations are produced through registered tools.

---

## System Architecture

### Main Components

| Component | File | Purpose |
|-----------|------|---------|
| **API Router** | `backend/app/routers/agent.py` | HTTP endpoints: `/agent`, `/agent/stream` |
| **VoltStream Agent Entry** | `backend/app/agents/voltstream_agent.py` | Creates session context and starts the ADK workflow |
| **ADK Runner** | `backend/app/agents/runner.py` | Runs the root agent, captures tool calls, observations, workflow, and trace |
| **Orchestrator Agent** | `backend/app/agents/orchestrator_agent.py` | Root coordinator that routes requests to specialists or direct tools |
| **Analyst Agent** | `backend/app/agents/analyst_agent.py` | Specialist for energy history, peaks, trends, and usage summaries |
| **Advisor Agent** | `backend/app/agents/advisor_agent.py` | Specialist for optimization recommendations and saving actions |
| **Agent Prompts** | `backend/app/agents/prompts.py` | Instructions for Orchestrator, Analyst, and Advisor behavior |
| **Tooling Helpers** | `backend/app/agents/tooling.py` | Tool naming and trace callback helpers |
| **Agent Context** | `backend/app/agents/context.py` | Context variables for DB access and trace recording during tool calls |
| **Session Manager** | `backend/app/services/session_manager.py` | Stores recent turns and resolves references such as "it" or "that device" |
| **Device Tools** | `backend/app/tools/device_tools.py` | Toggle, status, active devices, create, and delete operations |
| **Energy Tools** | `backend/app/tools/energy_tools.py` | Active load calculation and energy-saving recommendations |
| **Analytics Tools** | `backend/app/tools/analytics_tools.py` | Usage history, peak usage, and pattern summaries |

---

## How The Multi-Agent System Works

### Request Lifecycle

```text
User Request
    |
    v
POST /agent or POST /agent/stream
    |
    v
run_voltstream_agent()
    |
    v
Session context and reference resolution
    |
    v
run_adk_agent()
    |
    v
Orchestrator Agent
    |
    +--> Direct device tool for operational actions
    |
    +--> Analyst Agent for history, trends, peaks, and usage analysis
    |
    +--> Advisor Agent for recommendations and optimization
    |
    v
Tool observations and specialist outputs
    |
    v
Final response + workflow + trace
```

### Agent Loop

The root Orchestrator follows an ADK tool-using loop:

1. **Plan**: Interpret the user's natural language request.
2. **Route**: Decide whether to call a direct tool or delegate to a specialist agent.
3. **Execute**: Run the selected tool or specialist agent through ADK.
4. **Observe**: Read the returned tool result or specialist output.
5. **Synthesize**: Produce a concise final answer for the user.

### Example: Device Operation

```text
User: "Turn off the AC"
    |
    v
Orchestrator Agent
    |
    v
toggle_device(device_name="AC", state="off")
    |
    v
Device tool updates database and returns observation
    |
    v
Response: "Air Conditioning is now off."
```

For device toggling, the Orchestrator does not delegate to Analyst or Advisor. It calls `toggle_device` directly because the request is operational.

### Example: Usage Analysis

```text
User: "What was my peak usage last week?"
    |
    v
Orchestrator Agent
    |
    v
Analyst Agent
    |
    v
calculate_peak_usage(period="7d")
    |
    v
Response with peak window, peak kWh, and top contributing device
```

### Example: Recommendation

```text
User: "How can I reduce my energy consumption?"
    |
    v
Orchestrator Agent
    |
    v
Advisor Agent
    |
    v
recommend_energy_saving()
    |
    v
Response with prioritized saving recommendations
```

---

## Agent Routing Approach

### Routing Rules

The Orchestrator prompt defines the routing behavior:

| Request Type | Agent / Tool Used | Reason |
|--------------|-------------------|--------|
| Turn a device on or off | Orchestrator direct `toggle_device` tool | Operational state change |
| Get one device status | Orchestrator direct `get_device_status` tool | Current state lookup |
| List active devices | Orchestrator direct `get_active_devices` tool | Current state lookup |
| Create a device | Orchestrator direct `create_device` tool | Device inventory operation |
| Delete a device | Orchestrator direct `delete_device` tool | Device inventory operation |
| Ask about past usage | Analyst Agent | Requires historical data inspection |
| Ask about peaks or trends | Analyst Agent | Requires analytics tools |
| Ask for saving advice | Advisor Agent | Requires optimization reasoning |
| Ask for analysis then advice | Analyst Agent, then Advisor Agent | Analysis grounds the recommendation |

### Why This Design?

| Benefit | Description |
|---------|-------------|
| Clear ownership | Each specialist has a focused responsibility |
| Safer operations | Device mutations stay behind explicit tools |
| Better traceability | Workflow and trace capture each tool call and delegation |
| Stronger answers | Recommendations can be grounded in current state or historical analysis |
| Easier extension | New specialists or tools can be added without rewriting the entire system |

---

## Agent Responsibilities And Tools

### Orchestrator Agent

**File**: `backend/app/agents/orchestrator_agent.py`

**Purpose**: Root coordinator for the VoltStream multi-agent team.

**Responsibilities**:

- Receive the user request from the ADK runner.
- Decide whether to call a direct tool or delegate to a specialist.
- Use direct device tools for operational requests.
- Pass useful context between Analyst and Advisor when needed.
- Synthesize the final response.

**Registered Tools**:

| Tool | Type | Description |
|------|------|-------------|
| `analyst_agent` | `AgentTool` | Delegates analysis tasks to Analyst Agent |
| `advisor_agent` | `AgentTool` | Delegates recommendation tasks to Advisor Agent |
| `toggle_device` | `FunctionTool` | Turns a device on or off |
| `get_device_status` | `FunctionTool` | Reads status, room, category, health, and power |
| `get_active_devices` | `FunctionTool` | Lists currently active devices |
| `create_device` | `FunctionTool` | Adds a smart-home device |
| `delete_device` | `FunctionTool` | Removes a smart-home device |

### Analyst Agent

**File**: `backend/app/agents/analyst_agent.py`

**Purpose**: Specialist for historical and analytical energy questions.

**Responsibilities**:

- Inspect usage history for `24h`, `7d`, `30d`, or `all`.
- Calculate peak usage windows.
- Identify top consuming devices.
- Summarize historical usage patterns.
- Use active device state when present-state context helps analysis.

**Registered Tools**:

| Tool | Description |
|------|-------------|
| `get_usage_history` | Retrieves per-device energy usage history |
| `calculate_peak_usage` | Calculates the highest usage window and top contributing device |
| `summarize_usage_patterns` | Summarizes totals, peaks, and top device patterns |
| `get_active_devices` | Lists currently switched-on devices |
| `calculate_total_consumption` | Calculates current active wattage |

### Advisor Agent

**File**: `backend/app/agents/advisor_agent.py`

**Purpose**: Specialist for energy optimization and saving recommendations.

**Responsibilities**:

- Generate practical, prioritized saving advice.
- Inspect active devices before recommending action when needed.
- Use Orchestrator-provided analysis as grounding.
- Suggest device operations the user may approve next.

**Registered Tools**:

| Tool | Description |
|------|-------------|
| `get_active_devices` | Lists currently switched-on devices |
| `get_device_status` | Reads status and power details for a named device |
| `calculate_total_consumption` | Calculates current active wattage |
| `recommend_energy_saving` | Finds high-impact active devices to review |

---

## Configuration

### Environment Variables

| Variable | Default | Purpose | Location |
|----------|---------|---------|----------|
| `VERTEX_AI_PROJECT` | None | GCP project for Vertex AI Gemini | `backend/.env` |
| `VERTEX_AI_LOCATION` | `us-central1` | Vertex AI region | `backend/.env` |
| `GOOGLE_APPLICATION_CREDENTIALS` | None | Path to service account JSON | `backend/.env` |
| `VERTEX_AI_MODEL` | `gemini-2.5-flash` | Model used by Orchestrator, Analyst, and Advisor | `backend/.env` |

### Runtime Setup

`backend/app/agents/runner.py` configures the Vertex AI environment before warming up ADK:

```python
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.vertex_ai_project)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", settings.vertex_ai_location)
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## API Usage

### POST `/api/v1/agent`

Single request-response endpoint.

```bash
curl -X POST http://localhost:8000/api/v1/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Turn off the AC",
    "session_id": "vs-demo123"
  }'
```

**Response**:

```json
{
  "response": "Air Conditioning is now off.",
  "intent": "adk_multi_agent_workflow",
  "ai_used": true,
  "changed": true,
  "tool": "toggle_device",
  "observation": {
    "ok": true,
    "message": "Air Conditioning is now off.",
    "changed": true,
    "device": {
      "name": "Air Conditioning",
      "status": "off",
      "power_usage": 1500
    }
  },
  "workflow": [
    {
      "step": "TOOL_CALL",
      "agent": "Orchestrator",
      "tool": "toggle_device",
      "args": {
        "device_name": "AC",
        "state": "off"
      }
    }
  ],
  "trace": [],
  "session_id": "vs-demo123"
}
```

### POST `/api/v1/agent/stream`

Streaming endpoint for real-time trace and response tokens.

```bash
curl -X POST http://localhost:8000/api/v1/agent/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What was my peak usage last week?",
    "session_id": "vs-demo123"
  }'
```

**Response**: Server-Sent Events.

```text
event: status
data: {"state": "runner_started"}

event: trace
data: {"agent": "Orchestrator", "event": "delegation", "tool": "analyst_agent"}

event: trace
data: {"agent": "Analyst Agent", "event": "tool_call", "tool": "calculate_peak_usage"}

event: metadata
data: {"intent": "adk_multi_agent_workflow", "ai_used": true, ...}

event: token
data: {"token": "Your "}

event: done
data: {"response": "Your peak usage last week was ..."}
```

### Request Model

```python
class AgentRequest:
    message: str
    session_id: str | None
```

### Response Model

```python
class AgentResponse:
    response: str
    intent: str
    ai_used: bool
    changed: bool
    tool: str | None
    observation: dict | None
    workflow: list[dict]
    trace: list[dict]
    session_id: str
```

---

## Session Management

### Session Layers

VoltStream keeps two session layers:

| Layer | File | Purpose |
|-------|------|---------|
| Lightweight app session | `backend/app/services/session_manager.py` | Stores recent turns and last mentioned device |
| ADK session service | `backend/app/agents/runner.py` | Stores ADK session state through `InMemorySessionService` |

### What The App Session Stores

- `session_id`
- `user_id`
- `last_device_name`
- Last 6 conversation turns
- Last updated timestamp

### Reference Resolution

Before the request reaches ADK, `run_voltstream_agent()` resolves short references:

```text
Turn 1:
User: "Turn off the air conditioner"
Stored last_device_name = "Air Conditioner"

Turn 2:
User: "Turn it back on"
Resolved message = "Turn Air Conditioner back on"
```

### ADK Session State

The ADK runner creates session state containing:

```python
{
    "platform": "VoltStream",
    "conversation_context": context,
    "handoff_contract": "Orchestrator delegates specialist work through AgentTool and stores specialist outputs in session state."
}
```

---

## Performance Tuning

### Faster Response Times

| Goal | Change | Impact |
|------|--------|--------|
| Reduce cold-start latency | Call `warmup_adk()` on server startup | Builds agents and initializes ADK session service early |
| Avoid unnecessary specialist calls | Refine `ORCHESTRATOR_INSTRUCTION` | Keeps simple operations on direct tools |
| Reduce repeated setup | Reuse cached `_AGENT` and `_TOOLS` globals | Prevents rebuilding agents and tools per request |
| Stream progress | Use `/agent/stream` | Users see trace events before final response |

### Better Answer Quality

| Goal | Change | Impact |
|------|--------|--------|
| More accurate routing | Improve Orchestrator prompt | Better specialist selection |
| Better analysis | Improve Analyst prompt and analytics tools | Stronger historical explanations |
| Better recommendations | Improve Advisor prompt and energy tools | More practical saving advice |
| Better context | Store richer session context | Better multi-turn continuity |

### Observability

The system records:

- `workflow`: ADK function calls, observations, and final response.
- `trace`: user-facing progress messages for runner start, delegations, tool calls, observations, and final synthesis.
- `changed`: whether any tool confirmed a state mutation.
- `tool`: the most recent tool invoked.
- `observation`: the latest structured tool result.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "I could not start the ADK multi-agent workflow" | ADK import or runtime failure | Install backend requirements and check Google ADK dependency |
| Missing Vertex AI credentials | `GOOGLE_APPLICATION_CREDENTIALS` not set or invalid | Configure service account path in `backend/.env` |
| Wrong specialist selected | Orchestrator prompt is too broad or ambiguous | Refine `ORCHESTRATOR_INSTRUCTION` in `prompts.py` |
| Device not found | Fuzzy match score below threshold | Use a more specific device name or room name |
| Device did not change | Tool returned `changed: false` | Check observation message; device may already be in requested state |
| Multiple delete matches | Delete request matched more than one device | Ask user to specify room and device name |
| Missing DB in tool call | Context variable was not set | Ensure tool calls run inside `run_adk_agent()` with `current_db.set(db)` |
| Streaming shows no trace | No trace sink or no tool calls occurred | Check `/agent/stream` and verify tool/delegation path |
| Session context lost | In-memory sessions reset after restart | Use explicit device names after server restart |

### Debug Tips

**Check which agent was used**:

```json
{
  "workflow": [
    {
      "step": "TOOL_CALL",
      "agent": "Orchestrator",
      "tool": "analyst_agent"
    },
    {
      "step": "TOOL_CALL",
      "agent": "Analyst Agent",
      "tool": "calculate_peak_usage"
    }
  ]
}
```

**Check whether a device operation changed state**:

```json
{
  "changed": true,
  "tool": "toggle_device",
  "observation": {
    "ok": true,
    "changed": true,
    "message": "Air Conditioning is now off."
  }
}
```

**Read trace messages in streaming mode**:

```text
[Orchestrator] Received request. Starting ADK Runner orchestration...
[Orchestrator] Routing request to Analyst Agent...
[Analyst Agent] Calculating peak consumption...
[Orchestrator] Synthesizing final response for the user...
```
