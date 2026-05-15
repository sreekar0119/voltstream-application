import { Bot, FileText, UserRound } from "lucide-react";
import { motion } from "framer-motion";

export function ChatMessage({ message }) {
  const isUser = message.role === "user";
  const time = new Intl.DateTimeFormat([], { hour: "2-digit", minute: "2-digit" }).format(
    message.createdAt
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.24 }}
      className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser ? (
        <div className="mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-[8px] border border-cyan-300/20 bg-cyan-300/10 text-cyan-100">
          <Bot className="h-4 w-4" />
        </div>
      ) : null}
      <div className={`max-w-[78%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1`}>
        <div
          className={`rounded-[8px] px-3.5 py-2.5 text-sm leading-6 shadow-2xl ${
            isUser
              ? "bg-gradient-to-br from-cyan-300 to-teal-300 text-slate-950"
              : "border border-white/10 bg-slate-950/60 text-slate-100"
          }`}
        >
          {message.content}
        </div>
        {message.attachmentName ? (
          <div className="flex max-w-full items-center gap-1.5 rounded-[8px] border border-cyan-200/20 bg-cyan-300/10 px-2.5 py-1.5 text-xs text-cyan-50">
            <FileText className="h-3.5 w-3.5 shrink-0 text-cyan-200" />
            <span className="min-w-0 truncate">{message.attachmentName}</span>
          </div>
        ) : null}
        <span className="text-[11px] uppercase tracking-[0.14em] text-slate-500">{time}</span>
      </div>
      {isUser ? (
        <div className="mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-[8px] border border-white/10 bg-white/5 text-slate-200">
          <UserRound className="h-4 w-4" />
        </div>
      ) : null}
    </motion.div>
  );
}
