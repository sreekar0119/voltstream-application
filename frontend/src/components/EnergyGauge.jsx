import { motion } from "framer-motion";

export function EnergyGauge({ value, label, unit = "%", tone = "cyan" }) {
  const radius = 76;
  const circumference = 2 * Math.PI * radius;
  const progress = circumference - (Math.min(value, 100) / 100) * circumference;
  const color = tone === "green" ? "#5eead4" : tone === "amber" ? "#facc15" : "#22d3ee";

  return (
    <div className="relative flex min-h-64 items-center justify-center">
      <svg className="h-52 w-52 -rotate-90" viewBox="0 0 180 180">
        <circle cx="90" cy="90" r={radius} fill="transparent" stroke="rgba(148,163,184,.14)" strokeWidth="12" />
        <motion.circle
          cx="90"
          cy="90"
          r={radius}
          fill="transparent"
          stroke={color}
          strokeLinecap="round"
          strokeWidth="12"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: progress }}
          transition={{ duration: 1.3, ease: [0.22, 1, 0.36, 1] }}
          filter="url(#glow)"
        />
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      </svg>
      <div className="absolute text-center">
        <div className="text-5xl font-semibold text-white">{Math.round(value)}</div>
        <div className="mt-1 text-sm text-slate-400">{unit}</div>
        <div className="mt-3 text-xs font-medium uppercase tracking-[0.18em] text-slate-500">{label}</div>
      </div>
    </div>
  );
}
