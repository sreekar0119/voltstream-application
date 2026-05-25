# 🤖 VoltStream ADK Agent - Complete Code Explanation

## 📁 All Files Involved

| Layer | File | Purpose | Key Function |
|-------|------|---------|--------------|
| **API Entry** | `backend/app/routers/agent.py` | HTTP endpoints | `@router.post("/agent")` `@router.post("/agent/stream")` |
| **Orchestration** | `backend/app/agents/voltstream_agent.py` | Agent conductor | `run_voltstream_agent()` |
| **ADK Runner** | `backend/app/agents/runner.py` | Executes ADK agent | `run_adk_agent()` `build_voltstream_agent()` |
| **Session Mgmt** | `backend/app/agents/session_manager.py` | Conversation memory | `LightweightSession` `get_or_create()` |
| **Intent Router** | `backend/app/services/intent_router.py` | Fast path decision | `route_local_intent()` |
| **Prompts** | `backend/app/agents/prompts.py` | Agent instructions | `VOLTSTREAM_AGENT_INSTRUCTION` |
| **Tools** | `backend/app/tools/device_tools.py` | Device operations | `toggle_device()` `get_device_status()` etc |
| **Database** | `backend/app/models.py` | ORM models | `DeviceModel` table definition |
| **Frontend API** | `frontend/src/services/api.js` | API client | `deviceAgent()` `streamDeviceAgent()` |
| **Frontend UI** | `frontend/src/components/ai/DeviceAgentAssistant.jsx` | Chat interface | `submitCommand()` streaming handler |

---

## 🏗️ Layer-by-Layer Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         🌐 FRONTEND LAYER                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ DeviceAgentAssistant.jsx                                                    │
│                                                                              │
│ State:                                                                      │
│ ├─ open (dialog open/closed)                                               │
│ ├─ command (user input text)                                               │
│ ├─ messages (chat history)                                                 │
│ ├─ sessionId (conversation ID)                                             │
│ ├─ busy (loading state)                                                    │
│                                                                              │
│ Key Functions:                                                             │
│ ├─ createSessionId()        → Generate unique session                      │
│ ├─ getStoredSessionId()     → Persist session in localStorage              │
│ └─ submitCommand(event)     → Send message to backend                      │
│                                                                              │
│ Streaming Handler:                                                         │
│ ├─ onMetadata()   → Get ai_used flag + session_id                         │
│ ├─ onToken()      → Append each token to response                         │
│ └─ onDone()       → Mark completion                                        │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────┐
        │ api.js: streamDeviceAgent()             │
        │                                        │
        │ POST /api/v1/agent/stream              │
        │ {                                      │
        │   message: "turn off ac",              │
        │   session_id: "vs-xxx..."              │
        │ }                                      │
        └────────────────┬───────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    ⚡ FASTAPI ROUTER LAYER                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ backend/app/routers/agent.py                                               │
│                                                                              │
│ @router.post("/agent/stream")                                              │
│ async def agent_stream(payload: AgentRequest, db: Session):                │
│                                                                              │
│ 1. Validate Request                                                        │
│    ├─ message: min 1, max 1000 chars                                       │
│    ├─ session_id: optional, auto-generated                                 │
│    └─ raise HTTPException if invalid                                       │
│                                                                              │
│ 2. Create Session ID if missing                                            │
│    └─ session_manager.create_session_id() → "vs-xxxx"                      │
│                                                                              │
│ 3. Call _agent_event_stream()                                              │
│    └─ Returns AsyncIterator of SSE events                                  │
│                                                                              │
│ 4. Return StreamingResponse                                                │
│    ├─ media_type: "text/event-stream"                                      │
│    └─ Headers: Cache-Control, X-Accel-Buffering                            │
│                                                                              │
│ Event Stream Format:                                                       │
│ ├─ event: status                                                           │
│ │  data: {"state": "planning"}                                            │
│ │                                                                          │
│ ├─ event: metadata                                                        │
│ │  data: {"intent": "...", "ai_used": true, "session_id": "..."}         │
│ │                                                                          │
│ ├─ event: token (repeated)                                               │
│ │  data: {"token": "Air "}                                               │
│ │  data: {"token": "Conditioning "}                                      │
│ │  ...                                                                    │
│ │                                                                          │
│ └─ event: done                                                             │
│    data: {"response": "Air Conditioning has been turned off"}              │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                  🤖 AGENT ORCHESTRATION LAYER                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ backend/app/agents/voltstream_agent.py                                      │
│                                                                              │
│ async def run_voltstream_agent(db, message, session_id):                   │
│                                                                              │
│ STEP 1: Get/Create Session                                                 │
│ ├─ session = session_manager.get_or_create(session_id)                     │
│ ├─ Load from memory: session_id + user_id                                  │
│ └─ Contains: last_device_name, recent_turns history                        │
│                                                                              │
│ STEP 2: Resolve Pronouns                                                   │
│ ├─ resolved_message = session_manager.resolve_references(message, session) │
│ ├─ If message contains "it" or "its":                                      │
│ │  └─ Replace with session.last_device_name                               │
│ └─ Example: "turn it off" → "turn AC off"                                  │
│                                                                              │
│ STEP 3: Route Intent                                                       │
│ ├─ plan = route_local_intent(resolved_message)                             │
│ ├─ Returns: IntentPlan {intent, tool, args, deterministic, confidence}     │
│ └─ Checks 9 regex patterns (see next layer)                                │
│                                                                              │
│ STEP 4: Decide Execution Path                                              │
│ │                                                                          │
│ ├─ IF deterministic AND plan.tool:                                        │
│ │  │                                                                      │
│ │  └─ LOCAL PATH (Fast)                                                   │
│ │     ├─ observation = execute_local_tool(db, plan)                       │
│ │     ├─ Response: {ok, message, changed}                                 │
│ │     └─ Total time: ~100ms                                               │
│ │                                                                          │
│ ├─ ELSE:                                                                   │
│ │  │                                                                      │
│ │  └─ ADK PATH (Smart)                                                    │
│ │     ├─ adk_result = await run_adk_agent(...)                            │
│ │     ├─ Calls Google ADK with tools                                      │
│ │     └─ Total time: 1-3 seconds                                          │
│ │                                                                          │
│ STEP 5: Store Session Context                                              │
│ ├─ session.remember(message, response, observation)                        │
│ ├─ Updates: last_device_name, recent_turns                                 │
│ └─ Keeps last 6 turns for context                                          │
│                                                                              │
│ STEP 6: Return Response                                                    │
│ └─ response = {                                                             │
│      "response": "...",                                                    │
│      "intent": "toggle_device",                                            │
│      "ai_used": false,                                                     │
│      "changed": true,                                                      │
│      "workflow": [...],                                                    │
│      "session_id": "vs-xxx"                                                │
│    }                                                                        │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                ┌───────────────┴────────────────┐
                │                                │
                ▼                                ▼
┌────────────────────────────────┐    ┌──────────────────────────────────────┐
│ ⚡ LOCAL FAST PATH              │    │ 🧠 ADK SMART PATH                    │
├────────────────────────────────┤    ├──────────────────────────────────────┤
│ ~100 milliseconds              │    │ 1-3 seconds                          │
│                                │    │                                      │
│ route_local_intent()           │    │ run_adk_agent()                      │
│ (intent_router.py)             │    │ (runner.py)                          │
│                                │    │                                      │
│ Regex Pattern Matching:        │    │ Creates ADK Runner:                  │
│ ├─ \b(turn on|switch on)\b     │    │ ├─ agent = build_voltstream_agent()  │
│ ├─ \b(turn off|switch off)\b   │    │ ├─ runner = Runner(agent=agent)      │
│ ├─ \b(show|list).*active\b     │    │ └─ Streams events                    │
│ ├─ \b(status|state)\b          │    │                                      │
│ ├─ \b(consumption|usage)\b     │    │ ADK Agent Loop:                      │
│ └─ (other patterns)            │    │ ├─ 1. PLAN: Analyze message         │
│                                │    │ ├─ 2. SELECT TOOL: Pick best tool    │
│ Result: IntentPlan {           │    │ ├─ 3. EXECUTE: Call tool             │
│   intent: "toggle_device",     │    │ ├─ 4. OBSERVE: Get result            │
│   tool: "toggle_device",       │    │ └─ 5. RESPOND: Generate response     │
│   args: {...},                 │    │                                      │
│   deterministic: true,         │    │ Yields events:                       │
│   confidence: 0.96             │    │ ├─ event: "content" (tool selected)  │
│ }                              │    │ ├─ event: "function_call"            │
│                                │    │ ├─ event: "function_response"        │
│ execute_local_tool()           │    │ └─ event: "is_final_response"        │
│ └─ Call tool immediately       │    │                                      │
│                                │    │ Builds workflow log:                 │
│                                │    │ └─ [{step, result, ai_used...}]      │
└────────────────┬───────────────┘    └──────────────┬───────────────────────┘
                 │                                    │
                 └──────────────┬─────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         🔧 TOOL EXECUTION LAYER                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ backend/app/tools/device_tools.py                                           │
│                                                                              │
│ All tools are registered as FunctionTool objects with ADK                   │
│                                                                              │
│ Tool 1: toggle_device(device_name: str, state: str) → dict                 │
│ ├─ Find device via fuzzy matching                                          │
│ ├─ Check if state is "on" or "off"                                         │
│ ├─ Update DeviceModel.status in database                                   │
│ ├─ db.commit()                                                             │
│ └─ Return: {ok, changed, message, device}                                  │
│                                                                              │
│ Tool 2: get_device_status(device_name: str) → dict                         │
│ ├─ Find device via fuzzy matching                                          │
│ ├─ Query DeviceModel properties                                            │
│ └─ Return: {ok, device_data}                                               │
│                                                                              │
│ Tool 3: get_active_devices() → dict                                        │
│ ├─ Query DeviceModel WHERE status = "on"                                   │
│ └─ Return: {ok, devices: [...]}                                            │
│                                                                              │
│ Tool 4: calculate_total_consumption() → dict                               │
│ ├─ Query active devices                                                    │
│ ├─ Sum power_usage                                                         │
│ └─ Return: {ok, total_watts}                                               │
│                                                                              │
│ Tool 5: recommend_energy_saving() → dict                                   │
│ ├─ Analyze device usage patterns                                           │
│ ├─ Find high-power devices                                                 │
│ └─ Return: {ok, recommendations}                                           │
│                                                                              │
│ Tool 6: create_device(...) → dict                                          │
│ ├─ Validate inputs                                                         │
│ ├─ Create new DeviceModel                                                  │
│ ├─ db.add() + db.commit()                                                  │
│ └─ Return: {ok, changed, device}                                           │
│                                                                              │
│ Tool 7: delete_device(device_name: str) → dict                             │
│ ├─ Find device(s) matching name                                            │
│ ├─ If multiple matches: Ask clarification                                  │
│ ├─ If 1 match: Delete from database                                        │
│ └─ Return: {ok, changed, message}                                          │
│                                                                              │
│ ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│ Internal Fuzzy Matching (_score_device):                                    │
│ ├─ Compare query against:                                                  │
│ │  ├─ device.name                                                          │
│ │  ├─ room + name                                                          │
│ │  ├─ room + category                                                      │
│ │  └─ category                                                             │
│ ├─ Threshold: 0.7 (70% match confidence)                                   │
│ ├─ Short queries (1-2 chars): Word boundary matching                        │
│ │  └─ "AC" matches "living ac" (word boundary) NOT "HVAC"                 │
│ └─ Uses difflib.SequenceMatcher for ratio calculation                       │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         💾 DATABASE LAYER                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ SQLite + SQLAlchemy ORM                                                     │
│ File: backend/voltstream.db                                                │
│                                                                              │
│ DeviceModel Table:                                                         │
│ ├─ id: Integer (Primary Key)                                               │
│ ├─ name: String(255)          "Air Conditioning"                           │
│ ├─ category: String(50)       "Climate"                                    │
│ ├─ room: String(100)          "Living Room"                                │
│ ├─ status: String(20)         "on" or "off"                                │
│ ├─ power_usage: Integer       2500 (watts)                                 │
│ ├─ health: Integer            95 (0-100 score)                             │
│ ├─ daily_active_hours: Float  8.5                                          │
│ ├─ last_seen: DateTime                                                     │
│ ├─ created_at: DateTime                                                    │
│ └─ updated_at: DateTime                                                    │
│                                                                              │
│ SQL Queries Generated:                                                     │
│ ├─ SELECT * FROM device WHERE status = 'on'                                │
│ ├─ UPDATE device SET status = ? WHERE id = ?                               │
│ ├─ INSERT INTO device (name, category, ...) VALUES (...)                   │
│ └─ DELETE FROM device WHERE id = ?                                         │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    🎛️ SESSION MANAGEMENT LAYER                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ backend/app/agents/session_manager.py                                      │
│                                                                              │
│ LightweightSession Dataclass:                                              │
│ ├─ session_id: "vs-a1b2c3d4e5f6"                                           │
│ ├─ user_id: "voltstream-user"                                              │
│ ├─ last_device_name: "AC" ← Used for pronoun resolution                    │
│ ├─ recent_turns: [{user: "...", assistant: "..."}]  ← Last 6 turns        │
│ └─ updated_at: timestamp                                                   │
│                                                                              │
│ VoltStreamSessionManager Methods:                                          │
│                                                                              │
│ get_or_create(user_id, session_id):                                        │
│ ├─ Check if session exists in memory                                       │
│ ├─ If not: Create new LightweightSession                                   │
│ └─ Return session                                                          │
│                                                                              │
│ create_session_id():                                                       │
│ └─ Generate: "vs-" + 12 random hex chars                                   │
│                                                                              │
│ resolve_references(message, session):                                      │
│ ├─ If message contains "it", "its", "that device":                         │
│ │  └─ Replace with session.last_device_name                               │
│ └─ Example:                                                                │
│    - Before: "turn it off"                                                 │
│    - After: "turn AC off"                                                  │
│                                                                              │
│ session.remember(message, response, observation):                          │
│ ├─ If observation has device data:                                         │
│ │  └─ session.last_device_name = device.name                               │
│ ├─ Append {user: message, assistant: response} to recent_turns             │
│ ├─ Keep only last 6 turns (prune older)                                    │
│ └─ Update timestamp                                                        │
│                                                                              │
│ Storage: In-memory Python dict                                             │
│ Key: (user_id, session_id)                                                 │
│ Value: LightweightSession object                                           │
│                                                                              │
│ Lifetime: Until server restarts (consider persistent storage for prod)     │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    📋 RESPONSE BUILDER LAYER                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Build Complete Response:                                                   │
│                                                                              │
│ return {                                                                   │
│   "response": "AC turned on",                                              │
│   "intent": "toggle_device",                                               │
│   "tool": "toggle_device",                                                 │
│   "ai_used": false,                                                        │
│   "changed": true,                                                         │
│   "observation": {                                                         │
│     "ok": true,                                                            │
│     "message": "AC turned on",                                             │
│     "changed": true,                                                       │
│     "device": {                                                            │
│       "id": 1,                                                             │
│       "name": "AC",                                                        │
│       "status": "on",                                                      │
│       "power_usage": 2500                                                  │
│     }                                                                      │
│   },                                                                       │
│   "workflow": [                                                            │
│     {"step": "INPUT", "result": "turn on ac", "channel": "text"},         │
│     {"step": "LOCAL_INTENT_ROUTER", "result": "toggle_device", ...},      │
│     {"step": "DIRECT_TOOL_EXECUTION", "result": "toggle_device"},         │
│     {"step": "OBSERVATION", "result": {...}},                             │
│     {"step": "RESPOND", "result": "AC turned on"}                          │
│   ],                                                                       │
│   "session_id": "vs-a1b2c3d4e5f6"                                          │
│ }                                                                           │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    📤 FRONTEND STATE UPDATE LAYER                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ frontend/src/components/ai/DeviceAgentAssistant.jsx                        │
│                                                                              │
│ Streaming Event Handler:                                                   │
│                                                                              │
│ const result = await api.streamDeviceAgent(current, sessionId, {           │
│                                                                              │
│   onMetadata: (metadata) => {                                              │
│     // Received: {intent, ai_used, session_id, changed, ...}              │
│     if (metadata.session_id !== sessionId) {                               │
│       window.localStorage.setItem(SESSION_KEY, metadata.session_id)        │
│       setSessionId(metadata.session_id)                                    │
│     }                                                                      │
│     setMessages(prev => prev.map(msg =>                                    │
│       msg.id === assistantId                                               │
│         ? {...msg, aiUsed: metadata.ai_used}  ← Show "Vertex AI" badge    │
│         : msg                                                              │
│     ))                                                                     │
│   },                                                                       │
│                                                                              │
│   onToken: (token) => {                                                    │
│     // Received: "AC ", "turned ", "on"                                    │
│     setMessages(prev => prev.map(msg =>                                    │
│       msg.id === assistantId                                               │
│         ? {...msg, content: `${msg.content}${token}`}  ← Append            │
│         : msg                                                              │
│     ))                                                                     │
│   }                                                                        │
│ })                                                                         │
│                                                                              │
│ Final Response:                                                            │
│ if (result.changed) {                                                      │
│   window.dispatchEvent(                                                    │
│     new CustomEvent("voltstream:devices-updated", {detail: result})        │
│   )  ← Tell other components to refresh device list                        │
│ }                                                                           │
│                                                                              │
│ UI Updates:                                                                │
│ ├─ Display message in chat bubble                                          │
│ ├─ Show "Vertex AI" or "Local" badge                                       │
│ ├─ Update device cards if changed=true                                     │
│ ├─ Stop loading spinner                                                    │
│ └─ Keep scrollbar at bottom                                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Message Flow: Example

**User says: "Turn off the Air Conditioning"**

```
TIME    COMPONENT                STATE/ACTION
────────────────────────────────────────────────────────────────────
0ms     Frontend                 User types in ChatInput
        DeviceAgentAssistant     ├─ command = "Turn off the Air Conditioning"
                                 └─ Click Send button

5ms     Frontend Handler         ├─ submitCommand() called
        submitCommand()          ├─ assistantId = `assistant-${timestamp}`
                                 └─ Add user message to state

10ms    Frontend UI              ├─ Display user message in chat
        ChatMessage              └─ Show loading indicator

15ms    Frontend API Call        ├─ api.streamDeviceAgent(
        api.js                   │   "Turn off the Air Conditioning",
                                 │   "vs-a1b2c3d4e5f6",
                                 │   {onMetadata, onToken}
                                 └─ )

20ms    HTTP POST                ├─ Request to /api/v1/agent/stream
        Network                  └─ Headers: Content-Type: application/json

25ms    Backend Router           ├─ @router.post("/agent/stream")
        agent.py                 ├─ payload.message = "Turn off the Air Conditioning"
                                 ├─ payload.session_id = "vs-a1b2c3d4e5f6"
                                 └─ Validate with Pydantic

30ms    Session Manager          ├─ session_manager.get_or_create("vs-...")
        session_manager.py       ├─ Found existing session
                                 └─ Load: last_device_name = "AC"

35ms    Agent Orchestrator       ├─ run_voltstream_agent(
        voltstream_agent.py      │   message="Turn off the Air Conditioning",
                                 │   session_id="vs-..."
                                 └─ )

40ms    Resolve References       ├─ session_manager.resolve_references()
        (No pronouns here)       └─ Message unchanged: "Turn off the Air Conditioning"

45ms    Intent Router            ├─ route_local_intent("turn off the air conditioning")
        intent_router.py         ├─ Check Pattern: \b(turn off)\b ✅ MATCH!
                                 ├─ Extract device: "air conditioning"
                                 └─ Plan: {
                                 │   intent: "toggle_device",
                                 │   tool: "toggle_device",
                                 │   args: {device_name: "air conditioning", state: "off"},
                                 │   deterministic: True,
                                 │   confidence: 0.96
                                 └─ }

50ms    Deterministic Check      ├─ plan.deterministic == True? ✅ YES
        voltstream_agent.py      ├─ plan.tool exists? ✅ YES
                                 └─ → LOCAL PATH (not ADK)

55ms    Execute Local Tool       ├─ execute_local_tool(db, plan)
        intent_router.py         ├─ Plan: toggle_device with args
                                 └─ → device_tools.toggle_device()

60ms    Fuzzy Matching           ├─ find_device(db, "air conditioning")
        device_tools.py          ├─ Query all devices
                                 ├─ Score "air conditioning" against each:
                                 │  - "Air Conditioning": 1.0 ✅ PERFECT MATCH
                                 │  - "AC": 0.65 (below 0.7 threshold)
                                 │  - "HVAC": 0.58 (below threshold)
                                 └─ Return best: Device(id=5, name="Air Conditioning")

65ms    Database Query           ├─ device = db.query(DeviceModel).get(5)
        SQLAlchemy              └─ Found: {name: "Air Conditioning", status: "on"}

70ms    Toggle Device           ├─ Check state: "off" is valid ✅
        toggle_device()         ├─ device.status = "off"
                                ├─ device.updated_at = now()
                                ├─ db.commit()
                                └─ Return: {
                                 │   ok: True,
                                 │   changed: True,
                                 │   message: "Air Conditioning turned off",
                                 │   device: {...}
                                 └─ }

80ms    Build Response          ├─ response = {
        voltstream_agent.py     │   response: "Air Conditioning turned off",
                                │   intent: "toggle_device",
                                │   ai_used: False,
                                │   changed: True,
                                │   tool: "toggle_device",
                                │   observation: {...},
                                │   workflow: [
                                │     {step: "INPUT", result: "..."},
                                │     {step: "LOCAL_INTENT_ROUTER", result: "toggle_device"},
                                │     {step: "DIRECT_TOOL_EXECUTION", result: "toggle_device"},
                                │     {step: "OBSERVATION", result: {...}},
                                │     {step: "RESPOND", result: "Air Conditioning turned off"}
                                │   ],
                                │   session_id: "vs-a1b2c3d4e5f6"
                                └─ }

85ms    Remember Session        ├─ session.remember(
        session_manager.py      │   message="Turn off the Air Conditioning",
                                │   response="Air Conditioning turned off",
                                │   observation={device: {name: "Air Conditioning"}}
                                ├─ )
                                ├─ Updates: last_device_name = "Air Conditioning"
                                ├─ Appends to recent_turns
                                └─ (Now next message "turn it off" will resolve to "Air Conditioning")

90ms    Stream Response         ├─ SSE Event 1:
        agent.py                │ event: status
                                │ data: {"state": "planning"}
                                │
                                ├─ SSE Event 2:
                                │ event: metadata
                                │ data: {
                                │   "intent": "toggle_device",
                                │   "ai_used": false,
                                │   "session_id": "vs-a1b2c3d4e5f6",
                                │   "changed": true
                                │ }
                                │
                                ├─ SSE Event 3-10 (tokens):
                                │ event: token
                                │ data: {"token": "Air "}
                                │ event: token
                                │ data: {"token": "Conditioning "}
                                │ event: token
                                │ data: {"token": "turned "}
                                │ event: token
                                │ data: {"token": "off"}
                                │
                                └─ SSE Event N+1:
                                  event: done
                                  data: {"response": "Air Conditioning turned off"}

100ms   Frontend Handler        ├─ onMetadata(metadata) called
        submitCommand()         ├─ setSessionId() if new
                                ├─ setMessages() to update aiUsed badge: "Local" ✅
                                └─ assistantId stored

105ms   Frontend Token Stream   ├─ onToken("Air ") → append
        submitCommand()         ├─ onToken("Conditioning ") → append
                                ├─ onToken("turned ") → append
                                ├─ onToken("off") → append
                                └─ Message gradually builds up in real-time

110ms   Frontend UI Update      ├─ ChatMessage component renders:
        ChatMessage             │  "Air Conditioning turned off"
                                └─ Typing indicator disappears

115ms   Device Refresh          ├─ result.changed == true ✅
        DeviceAgentAssistant    ├─ window.dispatchEvent("voltstream:devices-updated")
                                └─ Other components (device cards) refresh

120ms   Final State             ├─ Chat shows user message + AI response
        Frontend Complete       ├─ Device card shows: "Air Conditioning: OFF" ✅
                                ├─ "Local" badge visible (not "Vertex AI")
                                ├─ Next message can use "turn it back on"
                                └─ User sees smooth streaming response

⏱️  TOTAL TIME: ~120ms (0.12 seconds) ✅ FAST!
```

---

## 🎯 Key Code Sections

### 1️⃣ Frontend Streaming Handler
```javascript
// frontend/src/components/ai/DeviceAgentAssistant.jsx

async function submitCommand(event) {
  event.preventDefault()
  if (!command.trim() || busy) return
  
  const current = command.trim()
  const assistantId = `assistant-${Date.now()}`
  setBusy(true)
  setCommand("")
  
  // Add messages to state
  setMessages(prev => [
    ...prev,
    { id: `user-${Date.now()}`, role: "user", content: current },
    { id: assistantId, role: "assistant", content: "", aiUsed: null, streaming: true }
  ])
  
  try {
    // ← This calls the streaming endpoint
    const result = await api.streamDeviceAgent(current, sessionId, {
      
      // Called when metadata arrives
      onMetadata: (metadata) => {
        // Update badge: show "Vertex ADK" or "Local"
        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantId 
              ? { ...msg, aiUsed: metadata.ai_used }
              : msg
          )
        )
      },
      
      // Called for each token
      onToken: (token) => {
        // Append token to response
        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantId
              ? { ...msg, content: `${msg.content}${token}` }
              : msg
          )
        )
      }
    })
    
    // When done, refresh device list if changed
    if (result.changed) {
      window.dispatchEvent(
        new CustomEvent("voltstream:devices-updated", { detail: result })
      )
    }
  } finally {
    setBusy(false)
  }
}
```

### 2️⃣ Backend Orchestrator
```python
# backend/app/agents/voltstream_agent.py

async def run_voltstream_agent(db: Session, message: str, session_id: str):
    # Get session
    session = session_manager.get_or_create(session_id=session_id)
    
    # Resolve pronouns
    resolved_message = session_manager.resolve_references(message, session)
    
    # Route locally
    plan = route_local_intent(resolved_message)
    
    # Fast path?
    if plan.deterministic and plan.tool:
        observation = execute_local_tool(db, plan)
        response = observation.get("message")
    else:
        # Smart path (ADK)
        adk_result = await run_adk_agent(db, resolved_message, session_id=session_id)
        response = adk_result["response"]
        observation = adk_result.get("observation")
    
    # Remember for next turn
    session.remember(message, response, observation)
    
    # Return complete response
    return {
        "response": response,
        "intent": plan.intent,
        "ai_used": plan_used_ai,
        "changed": bool(observation.get("changed")),
        "session_id": session.session_id
    }
```

### 3️⃣ Tool Execution
```python
# backend/app/tools/device_tools.py

def toggle_device(db: Session, device_name: str, state: str) -> dict:
    """Turn smart-home device on or off."""
    
    # Validate state
    if state not in {"on", "off"}:
        return {"ok": False, "message": "State must be 'on' or 'off'"}
    
    # Find device (fuzzy match)
    device = find_device(db, device_name)
    if not device:
        return {"ok": False, "message": f"Device '{device_name}' not found"}
    
    # Check if already in state
    if device.status == state:
        return {
            "ok": True,
            "changed": False,
            "message": f"{device.name} already {state}"
        }
    
    # Update and commit
    device.status = state
    db.commit()
    
    # Return observation
    return {
        "ok": True,
        "changed": True,
        "message": f"{device.name} turned {state}",
        "device": {
            "id": device.id,
            "name": device.name,
            "status": state,
            "power_usage": device.power_usage
        }
    }

def _score_device(query: str, device: DeviceModel) -> float:
    """Fuzzy match scoring with 0.7 threshold."""
    
    target = _normalize(query)
    candidates = [
        _normalize(device.name),
        _normalize(f"{device.room} {device.name}"),
        _normalize(f"{device.room} {device.category}"),
        _normalize(device.category)
    ]
    
    scores = []
    for candidate in candidates:
        if target == candidate:
            scores.append(1.0)  # Perfect match
        elif target in candidate or candidate in target:
            # For short queries (1-2 chars), require word boundary
            if len(target) <= 2:
                if re.search(rf"\b{re.escape(target)}\b", candidate, re.IGNORECASE):
                    scores.append(0.95)
            else:
                scores.append(0.88)
        else:
            scores.append(SequenceMatcher(None, target, candidate).ratio())
    
    return max(scores or [0])
```

---

## ✅ Complete Agent Code Summary

**What It Does:**
1. User sends message via frontend
2. Backend validates and gets/creates session
3. Resolves pronouns using session context
4. Routes to local (fast) or ADK (smart) path
5. Executes tool if needed
6. Returns response with workflow trace
7. Streams tokens back to frontend
8. Frontend refreshes UI and devices

**Performance:**
- Local path: ~100ms
- ADK path: 1-3 seconds
- Streaming: Tokens arrive in real-time
- Session: Remembers last device for next message

**Files:**
- Frontend: api.js, DeviceAgentAssistant.jsx, ChatWindow.jsx, ChatMessage.jsx
- Backend: agent.py (router), voltstream_agent.py (orchestrator), runner.py (ADK), session_manager.py, intent_router.py, device_tools.py
- Config: prompts.py, models.py

---

**This is your complete ADK agent implementation!** ✨
