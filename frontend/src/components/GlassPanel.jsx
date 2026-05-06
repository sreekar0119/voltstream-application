import { motion } from "framer-motion";

export function GlassPanel({ children, className = "", delay = 0 }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className={`glass rounded-[8px] ${className}`}
    >
      {children}
    </motion.section>
  );
}
