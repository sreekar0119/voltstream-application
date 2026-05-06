import { Sparkles } from "lucide-react";

export function EmptyState({ title = "No data available", message = "VoltStream could not find a matching signal." }) {
  return (
    <div className="glass-soft flex min-h-56 flex-col items-center justify-center rounded-[8px] p-8 text-center">
      <Sparkles className="mb-4 h-8 w-8 text-cyan-200" />
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <p className="mt-2 max-w-md text-sm text-slate-400">{message}</p>
    </div>
  );
}
