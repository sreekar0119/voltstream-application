export function StatusPill({ status }) {
  const map = {
    optimal: "bg-emerald-300/10 text-emerald-200 ring-emerald-300/20",
    attention: "bg-yellow-300/10 text-yellow-100 ring-yellow-300/25",
    offline: "bg-rose-300/10 text-rose-100 ring-rose-300/25",
    idle: "bg-slate-300/10 text-slate-200 ring-slate-300/20",
    on: "bg-cyan-300/10 text-cyan-100 ring-cyan-300/20",
    off: "bg-slate-300/10 text-slate-300 ring-slate-300/20"
  };

  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ring-1 ${map[status] ?? map.idle}`}>
      {status}
    </span>
  );
}
