import { Bot, ShieldCheck, X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

import { api } from "../../services/api.js";
import { AssistantTabs } from "./AssistantTabs.jsx";
import { ChatInput } from "./ChatInput.jsx";
import { ChatMessage } from "./ChatMessage.jsx";
import { TypingIndicator } from "./TypingIndicator.jsx";

const starterMessages = {
  energy: [
    {
      id: "energy-welcome",
      role: "assistant",
      content: "Hey, this is Disha. How may I help you? I can tune your solar usage, appliance schedule, and smart-home energy strategy.",
      createdAt: new Date()
    }
  ],
  qa: [
    {
      id: "qa-welcome",
      role: "assistant",
      content: "Hey, this is Disha. How may I help you? Ask me anything from your uploaded PDFs, and I will cite the source.",
      createdAt: new Date()
    }
  ]
};

const placeholders = {
  energy: "Ask Gemini about energy...",
  qa: "Ask a question from your backend PDFs..."
};

export function ChatWindow({ onClose }) {
  const [activeTab, setActiveTab] = useState("energy");
  const [messages, setMessages] = useState(starterMessages);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading, activeTab]);

  function addMessage(tab, message) {
    setMessages((current) => ({
      ...current,
      [tab]: [...current[tab], message]
    }));
  }

  function revealAssistantMessage(tab, text, meta = {}) {
    const id = `${tab}-assistant-${Date.now()}`;
    const words = text.split(" ");
    addMessage(tab, { id, role: "assistant", content: "", createdAt: new Date(), ...meta });

    words.forEach((_, index) => {
      window.setTimeout(() => {
        setMessages((current) => ({
          ...current,
          [tab]: current[tab].map((message) =>
            message.id === id
              ? { ...message, content: words.slice(0, index + 1).join(" ") }
              : message
          )
        }));
      }, 14 * index);
    });
  }



  async function sendMessage(text) {
    const tab = activeTab;
    addMessage(tab, {
      id: `${tab}-user-${Date.now()}`,
      role: "user",
      content: text,
      createdAt: new Date()
    });
    setLoading(true);

    try {
      if (tab === "energy") {
        const response = await api.energyChat(text);
        revealAssistantMessage(tab, response.answer);
      } else {
        const response = await api.documentQa(text);
        const notInDocs = response.answer === "I don't have that information in the provided documents.";
        revealAssistantMessage(tab, response.answer, {
          notInDocs
        });
      }
    } catch (error) {
      revealAssistantMessage(
        tab,
        error.message || "VoltStream AI is temporarily unavailable. Check backend keys and services."
      );
    } finally {
      setLoading(false);
    }
  }

  const activeMessages = messages[activeTab];

  return (
    <motion.aside
      initial={{ opacity: 0, y: 24, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 18, scale: 0.96 }}
      transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
      className="glass fixed bottom-24 right-4 z-50 flex h-[min(720px,calc(100vh-7rem))] w-[calc(100vw-2rem)] max-w-[430px] flex-col overflow-hidden rounded-[8px] sm:right-6"
    >
      <div className="relative border-b border-white/10 p-4">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/70 to-transparent" />
        <div className="flex items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className="grid h-11 w-11 shrink-0 place-items-center rounded-[8px] bg-cyan-300/10 text-cyan-100 energy-glow">
              <Bot className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <h2 className="truncate text-base font-semibold text-white">VoltStream AI Assistant</h2>
              <div className="mt-1 flex items-center gap-2 text-xs text-slate-400">
                <span className="h-2 w-2 rounded-full bg-lime-300 shadow-[0_0_12px_rgba(190,242,100,0.75)]" />
                AI online
              </div>
            </div>
          </div>
          <button
            type="button"
            aria-label="Close assistant"
            title="Close assistant"
            onClick={onClose}
            className="grid h-9 w-9 shrink-0 place-items-center rounded-[8px] border border-white/10 bg-white/5 text-slate-300 transition hover:border-cyan-200/30 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="mt-4">
          <AssistantTabs activeTab={activeTab} onChange={setActiveTab} />
        </div>
      </div>

      <div
        ref={scrollRef}
        className="custom-scrollbar flex-1 space-y-4 overflow-y-auto bg-[radial-gradient(circle_at_20%_0%,rgba(34,211,238,0.12),transparent_18rem)] p-4"
      >
        <AnimatePresence initial={false}>
          {activeMessages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </AnimatePresence>
        {loading ? <TypingIndicator /> : null}
      </div>

      <div className="flex items-center gap-2 border-t border-white/10 px-4 py-2 text-xs text-slate-500">
        <ShieldCheck className="h-3.5 w-3.5 text-cyan-200" />
        {activeTab === "qa" ? "VoltStream AI" : "Gemini energy guidance"}
      </div>
      <ChatInput
        loading={loading}
        onSend={sendMessage}
        placeholder={placeholders[activeTab]}
      />
    </motion.aside>
  );
}
