import { AlertCircle, FileText, Loader2, Paperclip, Send, X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { useRef, useState } from "react";

export function ChatInput({
  onSend,
  loading,
  placeholder,
  pdfEnabled = false,
  attachedPdf,
  uploadError,
  onPdfSelect,
  onRemovePdf
}) {
  const [value, setValue] = useState("");
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  function submit(event) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setValue("");
  }

  function selectFile(event) {
    const file = event.target.files?.[0];
    if (file) {
      onPdfSelect?.(file);
    }
    event.target.value = "";
  }

  return (
    <form onSubmit={submit} className="border-t border-white/10 bg-slate-950/35 p-3">
      {pdfEnabled ? (
        <div className="mb-2 space-y-2">
          <div className="flex min-h-9 items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf,.pdf"
              onChange={selectFile}
              className="hidden"
            />
            <button
              type="button"
              aria-label="Attach PDF"
              title="Attach PDF"
              disabled={loading}
              onClick={() => fileInputRef.current?.click()}
              className="grid h-9 w-9 shrink-0 place-items-center rounded-[8px] border border-white/10 bg-white/[0.04] text-cyan-100 transition hover:border-cyan-200/35 hover:bg-cyan-300/10 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Paperclip className="h-4 w-4" />
            </button>

            <AnimatePresence mode="wait">
              {attachedPdf ? (
                <motion.div
                  key="pdf-badge"
                  initial={{ opacity: 0, y: 4, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -4, scale: 0.98 }}
                  className="flex min-w-0 flex-1 items-center gap-2 rounded-[8px] border border-cyan-200/20 bg-cyan-300/10 px-2.5 py-1.5 text-xs text-cyan-50"
                >
                  <FileText className="h-3.5 w-3.5 shrink-0 text-cyan-200" />
                  <span className="min-w-0 flex-1 truncate">{attachedPdf.name}</span>
                  <span className="shrink-0 rounded bg-slate-950/40 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-cyan-100">
                    PDF
                  </span>
                  <button
                    type="button"
                    aria-label="Remove PDF"
                    title="Remove PDF"
                    disabled={loading}
                    onClick={onRemovePdf}
                    className="grid h-6 w-6 shrink-0 place-items-center rounded-[6px] text-slate-300 transition hover:bg-white/10 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </motion.div>
              ) : (
                <motion.p
                  key="pdf-empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-xs text-slate-500"
                >
                  Attach one PDF for Gemini to read with this chat.
                </motion.p>
              )}
            </AnimatePresence>
          </div>

          <AnimatePresence>
            {uploadError ? (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                className="flex items-center gap-2 rounded-[8px] border border-rose-300/20 bg-rose-400/10 px-3 py-2 text-xs text-rose-100"
              >
                <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                {uploadError}
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      ) : null}
      <div className="flex items-end gap-2">
        <textarea
          ref={inputRef}
          rows={1}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) submit(event);
          }}
          placeholder={placeholder}
          className="custom-scrollbar min-h-10 flex-1 resize-none rounded-[8px] border border-white/10 bg-white/[0.04] px-3 py-2.5 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-200/40 focus:ring-2 focus:ring-cyan-300/10"
        />
        <button
          type="submit"
          aria-label="Send message"
          title="Send message"
          disabled={loading || !value.trim()}
          className="grid h-10 w-10 shrink-0 place-items-center rounded-[8px] bg-gradient-to-br from-cyan-300 to-teal-300 text-slate-950 shadow-[0_0_28px_rgba(34,211,238,0.22)] transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </button>
      </div>
    </form>
  );
}
