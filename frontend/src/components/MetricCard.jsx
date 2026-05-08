import { motion } from "framer-motion";
import { number } from "../utils/format.js";

export function MetricCard({ label, value, unit, change = 0, showChange = false, icon: Icon, tone = "cyan" }) {
  const tones = {
    cyan: "from-cyan-300/25 to-blue-400/10 text-cyan-100",
    blue: "from-blue-300/20 to-cyan-400/10 text-blue-100",
    green: "from-emerald-300/20 to-lime-300/10 text-emerald-100",
    amber: "from-yellow-300/20 to-orange-400/10 text-yellow-100"
  };

  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ type: "spring", stiffness: 300, damping: 24 }}
      className="glass-soft rounded-[8px] p-4"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">{label}</p>
          <div className="mt-4 flex items-end gap-2">
            <span className="text-3xl font-semibold text-white">{typeof value === "number" ? number(value) : value}</span>
            <span className="pb-1 text-sm text-slate-400">{unit}</span>
          </div>
        </div>
        {Icon ? (
          <div className={`rounded-[8px] bg-gradient-to-br p-2.5 ${tones[tone]}`}>
            <Icon className="h-5 w-5" />
          </div>
        ) : null}
      </div>
      {showChange ? (
        <div className={`mt-4 flex items-center gap-1 text-xs ${Number(change) >= 0 ? "text-emerald-200" : "text-rose-200"}`}>
          <span>{Math.abs(Number(change)).toFixed(1)} since last signal</span>
        </div>
      ) : null}
    </motion.div>
  );
}
