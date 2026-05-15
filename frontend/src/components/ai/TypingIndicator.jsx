export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="glass-soft flex items-center gap-2 rounded-[8px] px-3 py-2 text-cyan-100">
        <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300 [animation-delay:-0.2s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-teal-300 [animation-delay:-0.1s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-lime-200" />
      </div>
    </div>
  );
}
