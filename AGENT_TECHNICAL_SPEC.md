# VoltStream Agent Technical Spec

## Scope
This document details the VoltStream agent architecture, the agent loop behavior, and the concrete files and components that implement the system.

## Agent Definition And Type
- Name: Disha (VoltStream ADK agent).
- Type: Tool-using agent (function-calling) built with Google ADK.
- Class: `google.adk.agents.Agent`.
- Tools: `google.adk.tools.FunctionTool` wrappers around Python functions.
- Session: `google.adk.sessions.InMemorySessionService` (in-memory; not persistent).
- Model: Gemini via Vertex AI when configured; default `gemini-2.5-flash`.

## Agent Loop (Detailed)
The ADK agent loop is tool-first and event-driven:
1. PLAN
   - Interpret the request and decide if tool usage is required.
   - Extract device entities (name, room, category, power usage).
2. SELECT TOOL
   - Choose the best tool (toggle, status, active devices, etc.).
3. EXECUTE TOOL
   - Run the selected tool via a FunctionTool wrapper.
4. OBSERVE RESULT
   - Read tool output (ok/changed/message/device payload).
   - Only report changes confirmed by tool output.
5. RESPOND
   - Produce a concise, operational response.

## Local Intent Router (Deterministic Path)
The local router catches common patterns and skips the LLM:
- File: [backend/app/services/intent_router.py](backend/app/services/intent_router.py)
- Logic: regex-based detection for toggle/status/active/consumption.
- Output: `IntentPlan` with confidence + tool arguments.

If a plan is deterministic, the tool is called directly:
- Tool executor: [backend/app/services/intent_router.py](backend/app/services/intent_router.py)
- Results are returned without ADK or LLM usage.

## ADK Runner (Reasoning Path)
- File: [backend/app/agents/runner.py](backend/app/agents/runner.py)
- Creates the agent with tools and prompt instructions.
- Initializes ADK sessions on demand.
- Streams tool-call and tool-response events.
- Builds a workflow trace of steps and outcomes.

## Prompt And Guardrails
- Prompt source: [backend/app/agents/prompts.py](backend/app/agents/prompts.py)
- Guardrails:
  - Never mutate DB directly.
  - Use tools for any state change.
  - Ask for clarification when ambiguous.
  - Verify devices before destructive actions.

## Session Management
- File: [backend/app/agents/session_manager.py](backend/app/agents/session_manager.py)
- Tracks last device name and recent turns.
- Resolves references like "it" or "that device".
- In-memory sessions reset on server restart.

## Tooling Layer
### Device Tools
- File: [backend/app/tools/device_tools.py](backend/app/tools/device_tools.py)
- Functions:
  - `toggle_device`
  - `get_device_status`
  - `get_active_devices`
  - `create_device`
  - `delete_device`
- Uses fuzzy matching to locate target devices.

### Energy Tools
- File: [backend/app/tools/energy_tools.py](backend/app/tools/energy_tools.py)
- Functions:
  - `calculate_total_consumption`
  - `recommend_energy_saving`

## API Surface
- REST endpoint: POST `/api/v1/agent`
- Streaming endpoint: POST `/api/v1/agent/stream`
- Router file: [backend/app/routers/agent.py](backend/app/routers/agent.py)

## Startup Behavior
- ADK warmup on startup: [backend/app/main.py](backend/app/main.py)
- Warmup method: [backend/app/agents/runner.py](backend/app/agents/runner.py)

## Observability
- Workflow trace is returned with every response.
- Steps include input, routing, tool calls, observations, and final response.
- The stream endpoint emits SSE events: status, metadata, token, done.

## Data Model
- Device model is defined in [backend/app/models.py](backend/app/models.py).
- The agent operates only on device data through tools.

## Failure Modes
- ADK dependency missing: runtime error surfaced in response.
- Tool errors: returned as safe error payloads with `ok: false`.
- Ambiguous delete: tool asks for clarification instead of deleting.
