import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, RadioTower } from "lucide-react";

export function NotFound() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="grid min-h-[70vh] place-items-center"
    >
      <div className="relative max-w-2xl text-center">
        <motion.div
          animate={{ opacity: [0.35, 0.85, 0.35], scale: [1, 1.04, 1] }}
          transition={{ duration: 3, repeat: Infinity }}
          className="absolute inset-0 -z-10 rounded-full bg-cyan-300/20 blur-3xl"
        />
        <div className="mx-auto grid h-20 w-20 place-items-center rounded-[8px] border border-cyan-300/25 bg-cyan-300/10 text-cyan-100">
          <RadioTower className="h-10 w-10" />
        </div>
        <p className="mt-8 text-sm font-semibold uppercase tracking-[0.28em] text-cyan-200">Signal lost</p>
        <h1 className="mt-4 text-6xl font-semibold text-white sm:text-8xl">404</h1>
        <p className="mx-auto mt-5 max-w-lg text-base leading-7 text-slate-400">
          This route is outside the VoltStream telemetry mesh. Return to the live home energy console.
        </p>
        <Link
          to="/"
          className="energy-glow mt-8 inline-flex items-center gap-2 rounded-[8px] bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to dashboard
        </Link>
      </div>
    </motion.div>
  );
}
