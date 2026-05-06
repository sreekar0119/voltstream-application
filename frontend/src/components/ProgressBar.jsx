import { motion } from "framer-motion";

export function ProgressBar({ value, max = 100, tone = "cyan" }) {
  const width = Math.min(100, (value / max) * 100);
  const colors = {
    cyan: "from-cyan-300 to-emerald-300",
    amber: "from-yellow-300 to-orange-300",
    rose: "from-rose-300 to-orange-300"
  };

  return (
    <div className="h-2.5 overflow-hidden rounded-full bg-slate-800">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${width}%` }}
        transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        className={`h-full rounded-full bg-gradient-to-r ${colors[tone]}`}
      />
    </div>
  );
}
