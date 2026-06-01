import { Cpu, Fan, Home, Lightbulb, PlugZap, Trash2 } from "lucide-react";
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

export function DeviceCard({ device, onToggle, onDelete, busy }) {
  const Icon = icons[device.category] ?? PlugZap;
  const active = device.status === "on";

  return (
    <motion.article
      layout
      whileHover={{ y: -5 }}
      className={`glass-soft rounded-[8px] p-2.5 transition ${active ? "energy-glow" : ""}`}
    >
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className={`grid h-9 w-9 place-items-center rounded-[8px] ${active ? "bg-cyan-300/10 text-cyan-100" : "bg-slate-800 text-slate-400"}`}>
            <Icon className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <h3 className="truncate text-sm font-semibold text-white">{device.name}</h3>
            <p className="truncate text-xs text-slate-400">
              {device.room && device.room !== "General" ? `${device.room} - ${device.category}` : device.category}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            title="Delete device"
            onClick={() => onDelete(device.id)}
            disabled={busy}
            className="grid h-[26px] w-[26px] place-items-center rounded-[8px] bg-white/5 text-slate-400 transition hover:bg-rose-400/10 hover:text-rose-100 disabled:opacity-60"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
          <Toggle checked={active} disabled={busy} size="sm" onChange={(next) => onToggle(device.id, next ? "on" : "off")} />
        </div>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-3">
        <div>
          <p className="text-[11px] text-slate-500">Load</p>
          <p className="mt-1 text-xs font-semibold text-white">{number(device.power_usage, 0)} W</p>
        </div>
        <div>
          <p className="text-[11px] text-slate-500">Hours</p>
          <p className="mt-1 text-xs font-semibold text-white">{device.daily_active_hours} h</p>
        </div>
        <div>
          <p className="text-[11px] text-slate-500">Health</p>
          <div className="mt-1">
            <StatusPill status={device.health} />
          </div>
        </div>
      </div>
    </motion.article>
  );
}
