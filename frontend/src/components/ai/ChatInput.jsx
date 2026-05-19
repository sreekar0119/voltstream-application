import { Loader2, Send } from "lucide-react";
import { useRef, useState } from "react";

export function ChatInput({
  onSend,
  loading,
  placeholder
}) {
  const [value, setValue] = useState("");
  const inputRef = useRef(null);

  function submit(event) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setValue("");
  }

  return (
    <form onSubmit={submit} className="border-t border-white/10 bg-slate-950/35 p-3">
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
