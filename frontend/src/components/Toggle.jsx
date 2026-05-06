import { motion } from "framer-motion";

export function Toggle({ checked, onChange, disabled }) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={`relative h-7 w-12 rounded-full p-1 transition ${
        checked ? "bg-cyan-300/80 shadow-[0_0_22px_rgba(34,211,238,.36)]" : "bg-slate-700"
      } ${disabled ? "opacity-60" : ""}`}
      aria-pressed={checked}
    >
      <motion.span
        layout
        transition={{ type: "spring", stiffness: 450, damping: 30 }}
        className="block h-5 w-5 rounded-full bg-white shadow-lg"
        style={{ marginLeft: checked ? 20 : 0 }}
      />
    </button>
  );
}
