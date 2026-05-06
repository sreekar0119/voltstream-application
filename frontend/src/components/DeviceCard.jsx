import { Cpu, Fan, Home, Lightbulb, PlugZap } from "lucide-react";
import { motion } from "framer-motion";
import { StatusPill } from "./StatusPill.jsx";
import { Toggle } from "./Toggle.jsx";
import { number } from "../utils/format.js";

const icons = {
  Climate: Fan,
  Lighting: Lightbulb,
  Energy: PlugZap,
  Kitchen: Home,
  Utility: Cpu
};

export function DeviceCard({ device, onToggle, busy }) {
  const Icon = icons[device.category] ?? PlugZap;
  const active = device.status === "on";

  return (
    <motion.article
      layout
      whileHover={{ y: -5 }}
      className={`glass-soft rounded-[8px] p-4 transition ${active ? "energy-glow" : ""}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className={`grid h-11 w-11 place-items-center rounded-[8px] ${active ? "bg-cyan-300/10 text-cyan-100" : "bg-slate-800 text-slate-400"}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold text-white">{device.name}</h3>
            <p className="text-sm text-slate-400">{device.category}</p>
          </div>
        </div>
        <Toggle checked={active} disabled={busy} onChange={(next) => onToggle(device.id, next ? "on" : "off")} />
      </div>
      <div className="mt-5 grid grid-cols-3 gap-3">
        <div>
          <p className="text-xs text-slate-500">Load</p>
          <p className="mt-1 text-sm font-semibold text-white">{number(device.power_usage, 0)} W</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Hours</p>
          <p className="mt-1 text-sm font-semibold text-white">{device.daily_active_hours} h</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Health</p>
          <div className="mt-1">
            <StatusPill status={device.health} />
          </div>
        </div>
      </div>
    </motion.article>
  );
}
