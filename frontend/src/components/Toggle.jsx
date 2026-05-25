import { motion } from "framer-motion";

export function Toggle({ checked, onChange, disabled, size = "md" }) {
  const isSmall = size === "sm";
  const trackClass = isSmall ? "h-6 w-10" : "h-7 w-12";
  const knobClass = isSmall ? "h-4 w-4" : "h-5 w-5";
  const knobOffset = isSmall ? 16 : 20;
  const offClass = "bg-slate-600/80 border border-white/10";

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={`relative rounded-full p-1 transition ${trackClass} ${
        checked ? "bg-cyan-300/80 shadow-[0_0_22px_rgba(34,211,238,.36)]" : offClass
      } ${disabled ? "opacity-60" : ""}`}
      aria-pressed={checked}
    >
      <motion.span
        layout
        transition={{ type: "spring", stiffness: 450, damping: 30 }}
        className={`block rounded-full bg-white shadow-lg ${knobClass}`}
        style={{ marginLeft: checked ? knobOffset : 0 }}
      />
    </button>
  );
}
