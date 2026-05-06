import { AlertTriangle } from "lucide-react";

export function AlertBanner({ children, tone = "cyan" }) {
  const tones = {
    cyan: "border-cyan-300/20 bg-cyan-300/10 text-cyan-100",
    amber: "border-yellow-300/25 bg-yellow-300/10 text-yellow-100",
    rose: "border-rose-300/25 bg-rose-300/10 text-rose-100"
  };

  return (
    <div className={`flex items-center gap-3 rounded-[8px] border px-4 py-3 ${tones[tone]}`}>
      <AlertTriangle className="h-4 w-4 shrink-0" />
      <p className="text-sm">{children}</p>
    </div>
  );
}
