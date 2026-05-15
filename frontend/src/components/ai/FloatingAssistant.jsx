import { Bot, Sparkles } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

import { ChatWindow } from "./ChatWindow.jsx";

export function FloatingAssistant() {
  const [open, setOpen] = useState(false);
  const [showGreeting, setShowGreeting] = useState(true);

  return (
    <>
      <AnimatePresence>
        {open ? <ChatWindow onClose={() => setOpen(false)} /> : null}
      </AnimatePresence>
      <AnimatePresence>
        {!open && showGreeting ? (
          <motion.div
            key="assistant-greeting"
            initial={{ opacity: 0, y: 8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-[88px] right-[78px] z-50 max-w-[240px] rounded-[12px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100 shadow-[0_12px_40px_rgba(15,23,42,0.45)] backdrop-blur sm:right-[96px]"
          >
            <span className="pointer-events-none absolute -right-2 bottom-5 h-4 w-4 rotate-45 rounded-[4px] border border-white/20 bg-slate-900/80 shadow-[0_6px_16px_rgba(15,23,42,0.35)]" />
            <button
              type="button"
              aria-label="Dismiss greeting"
              onClick={() => setShowGreeting(false)}
              className="absolute right-2 top-2 grid h-6 w-6 place-items-center rounded-[6px] text-slate-400 transition hover:bg-white/10 hover:text-white"
            >
              ×
            </button>
            <div className="flex items-start gap-2 pr-6">
              <span className="grid h-8 w-8 shrink-0 place-items-center rounded-[8px] bg-cyan-300/10 text-cyan-100">
                <Bot className="h-4 w-4" />
              </span>
              <div>
                <p className="text-sm font-semibold text-white">Hi, I'm Disha.</p>
                <p className="mt-1 text-xs text-slate-300">How may I help you?</p>
              </div>
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
      <motion.button
        type="button"
        aria-label={open ? "Close VoltStream AI Assistant" : "Open VoltStream AI Assistant"}
        title="VoltStream AI Assistant"
        onClick={() => setOpen((value) => !value)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.96 }}
        className="fixed bottom-5 right-4 z-50 grid h-16 w-16 place-items-center rounded-full border border-cyan-200/25 bg-slate-950/75 text-cyan-50 shadow-[0_0_42px_rgba(34,211,238,0.36)] backdrop-blur-2xl sm:right-6"
      >
        <span className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-300/30 via-teal-300/20 to-lime-200/20" />
        <span className="assistant-pulse absolute inset-[-7px] rounded-full border border-cyan-200/25" />
        <span className="relative grid h-12 w-12 place-items-center rounded-full bg-gradient-to-br from-cyan-300 to-teal-300 text-slate-950">
          {open ? <Sparkles className="h-6 w-6" /> : <Bot className="h-6 w-6" />}
        </span>
      </motion.button>
    </>
  );
}
