import { AnimatePresence, motion } from "framer-motion";
import { Bot, BrainCircuit, Cpu, GitBranch, Loader2, Mic, Send, Sparkles, X, Zap } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { api } from "../../services/api.js";

const SESSION_KEY = "voltstream-device-agent-session";
const DEVICE_MUTATION_TOOLS = new Set(["toggle_device", "create_device", "delete_device"]);

function createSessionId() {
  if (globalThis.crypto?.randomUUID) {
    return `vs-web-${globalThis.crypto.randomUUID()}`;
  }

  if (globalThis.crypto?.getRandomValues) {
    const bytes = new Uint32Array(4);
    globalThis.crypto.getRandomValues(bytes);
    return `vs-web-${Array.from(bytes, (value) => value.toString(16).padStart(8, "0")).join("")}`;
  }

  return `vs-web-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

function getStoredSessionId() {
  const existing = window.localStorage.getItem(SESSION_KEY);
  if (existing) return existing;
  const next = createSessionId();
  window.localStorage.setItem(SESSION_KEY, next);
  return next;
}

function shouldRefreshDevices(result) {
  if (result?.changed) return true;

  const workflowChanged = (result?.workflow ?? []).some((step) => DEVICE_MUTATION_TOOLS.has(step.tool));
  const traceChanged = (result?.trace ?? []).some((entry) => DEVICE_MUTATION_TOOLS.has(entry.tool));

  return workflowChanged || traceChanged;
}

export function DeviceAgentAssistant() {
  const [open, setOpen] = useState(false);
  const [command, setCommand] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [speechAvailable, setSpeechAvailable] = useState(false);
  const [listening, setListening] = useState(false);
  const [speechError, setSpeechError] = useState("");
  const [trace, setTrace] = useState([]);
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "assistant",
      content: "Agent online. I can operate devices, create appliances, remove devices, and optimize energy usage.",
      aiUsed: true
    }
  ]);
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    setSessionId(getStoredSessionId());
  }, []);

  useEffect(() => {
    const SpeechRecognition = globalThis.SpeechRecognition || globalThis.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechAvailable(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event?.results?.[0]?.[0]?.transcript || "";
      if (transcript) {
        setCommand(transcript);
        setSpeechError("");
        void sendCommand(transcript);
      }
    };

    recognition.onerror = (event) => {
      setSpeechError(event?.error ? `Mic error: ${event.error}` : "Mic error occurred.");
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognitionRef.current = recognition;
    setSpeechAvailable(true);

    return () => {
      recognitionRef.current?.abort();
      recognitionRef.current = null;
    };
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function sendCommand(nextCommand) {
    if (!nextCommand.trim() || busy) return;

    const current = nextCommand.trim();
    const assistantId = `assistant-${Date.now()}`;
    setBusy(true);
    setCommand("");
    setTrace([]);
    setMessages((prev) => [
      ...prev,
      { id: `user-${Date.now()}`, role: "user", content: current },
      { id: assistantId, role: "assistant", content: "", aiUsed: null, streaming: true }
    ]);

    try {
      const result = await api.streamDeviceAgent(current, sessionId, {
        onMetadata: (metadata) => {
          if (metadata.session_id && metadata.session_id !== sessionId) {
            window.localStorage.setItem(SESSION_KEY, metadata.session_id);
            setSessionId(metadata.session_id);
          }
          if (Array.isArray(metadata.trace) && metadata.trace.length) {
            setTrace(metadata.trace);
          }
          setMessages((prev) =>
            prev.map((msg) => (msg.id === assistantId ? { ...msg, aiUsed: metadata.ai_used } : msg))
          );
        },
        onTrace: (entry) => {
          setTrace((prev) => [...prev, entry]);
        },
        onToken: (token) => {
          setMessages((prev) =>
            prev.map((msg) => (msg.id === assistantId ? { ...msg, content: `${msg.content}${token}` } : msg))
          );
        }
      });

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? { ...msg, content: result.response || msg.content, aiUsed: result.ai_used, streaming: false }
            : msg
        )
      );
      if (shouldRefreshDevices(result)) {
        window.dispatchEvent(new CustomEvent("voltstream:devices-updated", { detail: result }));
      }
    } catch (error) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? {
                ...msg,
                content: error.message || "The text agent is unavailable.",
                aiUsed: false,
                streaming: false,
                error: true
              }
            : msg
        )
      );
    } finally {
      setBusy(false);
    }
  }

  async function submitCommand(event) {
    event.preventDefault();
    await sendCommand(command);
  }

  function toggleListening() {
    if (!speechAvailable || busy) return;
    const recognition = recognitionRef.current;
    if (!recognition) return;

    if (listening) {
      recognition.stop();
      setListening(false);
      return;
    }

    setSpeechError("");
    setListening(true);
    recognition.start();
  }

  return (
    <>
      <AnimatePresence>
        {open ? (
          <motion.section
            key="device-agent"
            initial={{ opacity: 0, y: 24, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 18, scale: 0.96 }}
            transition={{ duration: 0.24 }}
            className="fixed bottom-44 right-4 z-50 w-[calc(100vw-2rem)] max-w-[430px] overflow-hidden rounded-[14px] border border-cyan-200/20 bg-slate-950/88 shadow-[0_28px_90px_rgba(0,0,0,0.46),0_0_70px_rgba(34,211,238,0.18)] backdrop-blur-2xl sm:bottom-28 sm:right-28"
          >
            <div className="border-b border-white/10 bg-[radial-gradient(circle_at_20%_0%,rgba(125,249,255,0.16),transparent_36%),linear-gradient(135deg,rgba(8,47,73,0.82),rgba(2,6,23,0.94))] p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-cyan-200/80">VoltStream ADK Operator</p>
                  <h2 className="mt-1 text-lg font-semibold text-white">Energy command layer</h2>
                </div>
                <button
                  type="button"
                  title="Close text agent"
                  onClick={() => setOpen(false)}
                  className="grid h-9 w-9 place-items-center rounded-[8px] bg-white/5 text-slate-200 transition hover:bg-white/10"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-slate-300">
                <StatusPill icon={BrainCircuit} label="ADK tools" />
                <StatusPill icon={Cpu} label="Gemini" />
              </div>
            </div>

            <div className="space-y-3 p-4">
              <div
                ref={scrollRef}
                className="custom-scrollbar max-h-72 space-y-3 overflow-y-auto rounded-[8px] border border-cyan-200/10 bg-gradient-to-b from-slate-900/40 to-transparent p-3"
              >
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {msg.role === "assistant" && (
                      <div className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-cyan-300/16 text-cyan-100">
                        {msg.streaming ? <Sparkles className="h-4 w-4 animate-pulse" /> : <Bot className="h-4 w-4" />}
                      </div>
                    )}
                    <div
                      className={`max-w-[82%] rounded-[8px] px-3 py-2 text-sm leading-5 ${
                        msg.role === "user"
                          ? "bg-cyan-300/20 text-cyan-50"
                          : msg.error
                            ? "bg-rose-400/10 text-rose-100"
                            : "bg-cyan-300/[0.07] text-cyan-50"
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.content || "Planning..."}</p>
                      {msg.role === "assistant" && (
                        <div className="mt-1.5 flex items-center gap-1.5 text-xs text-slate-400">
                          {msg.streaming ? <Loader2 className="h-3 w-3 animate-spin" /> : <Cpu className="h-3 w-3" />}
                          {msg.aiUsed === null ? "Routing" : msg.aiUsed ? "Vertex ADK" : "Local"}
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="rounded-[8px] border border-cyan-200/10 bg-slate-950/45 p-3">
                <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-cyan-200/80">
                  <GitBranch className="h-3.5 w-3.5" />
                  Multi-agent trace
                </div>
                <div className="custom-scrollbar max-h-32 space-y-2 overflow-y-auto pr-1">
                  {trace.length ? (
                    trace.slice(-8).map((entry, index) => (
                      <div key={`${entry.event}-${index}`} className="grid grid-cols-[88px_1fr] gap-2 text-xs">
                        <span className="truncate rounded-[6px] bg-cyan-300/10 px-2 py-1 text-cyan-100">{entry.agent}</span>
                        <span className="min-w-0 rounded-[6px] bg-white/[0.04] px-2 py-1 text-slate-300">
                          {entry.message}
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="rounded-[6px] bg-white/[0.04] px-2 py-2 text-xs text-slate-500">
                      Waiting for the next ADK run.
                    </div>
                  )}
                </div>
              </div>

              <form onSubmit={submitCommand} className="flex gap-2">
                <input
                  value={command}
                  onChange={(event) => setCommand(event.target.value)}
                  placeholder="Type a smart-home command"
                  className="h-11 min-w-0 flex-1 rounded-[8px] border border-white/10 bg-slate-950/60 px-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                />
                <button
                  type="button"
                  onClick={toggleListening}
                  disabled={!speechAvailable || busy}
                  className={`grid h-11 w-11 place-items-center rounded-[8px] border transition disabled:opacity-60 ${
                    listening
                      ? "border-rose-200/40 bg-rose-400/20 text-rose-100"
                      : "border-white/10 bg-slate-950/60 text-slate-200 hover:bg-white/5"
                  }`}
                  title={speechAvailable ? (listening ? "Stop listening" : "Start voice input") : "Voice not supported"}
                >
                  <Mic className={`h-4 w-4 ${listening ? "animate-pulse" : ""}`} />
                </button>
                <button
                  type="submit"
                  disabled={busy}
                  className="grid h-11 w-11 place-items-center rounded-[8px] bg-cyan-300 text-slate-950 transition hover:bg-cyan-200 disabled:opacity-60"
                  title="Send command"
                >
                  {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                </button>
              </form>
              {speechError ? <p className="text-xs text-rose-200/80">{speechError}</p> : null}
            </div>
          </motion.section>
        ) : null}
      </AnimatePresence>

      <motion.button
        type="button"
        aria-label="Open VoltStream Device Agent"
        title="VoltStream Device Agent"
        onClick={() => setOpen((value) => !value)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.96 }}
        className="fixed bottom-24 right-4 z-50 grid h-16 w-16 place-items-center rounded-full border border-lime-200/25 bg-slate-950/75 text-cyan-50 shadow-[0_0_42px_rgba(190,242,100,0.24)] backdrop-blur-2xl sm:bottom-5 sm:right-28"
      >
        <span className="absolute inset-0 rounded-full bg-gradient-to-br from-lime-200/25 via-cyan-300/24 to-teal-300/20" />
        <span className="assistant-pulse absolute inset-[-7px] rounded-full border border-lime-200/20" />
        <span className="relative grid h-12 w-12 place-items-center rounded-full bg-gradient-to-br from-lime-200 to-cyan-300 text-slate-950">
          <Zap className="h-6 w-6" />
        </span>
      </motion.button>
    </>
  );
}

function StatusPill({ icon: Icon, label }) {
  return (
    <div className="flex min-w-0 items-center gap-1.5 rounded-[8px] border border-white/10 bg-white/[0.04] px-2 py-1.5">
      <Icon className="h-3.5 w-3.5 shrink-0 text-cyan-200" />
      <span className="truncate">{label}</span>
    </div>
  );
}
