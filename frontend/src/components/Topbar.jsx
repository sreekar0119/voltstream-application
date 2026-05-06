import { NavLink, useLocation } from "react-router-dom";
import { Activity, BarChart3, Gauge, Menu, ReceiptText, Zap } from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";

const titles = {
  "/": ["Live Dashboard", "Real-time solar, battery, and grid orchestration"],
  "/analytics": ["Usage History", "Hourly consumption, generation, and cost intelligence"],
  "/devices": ["Smart Control", "Appliance telemetry and circuit-level command"],
  "/billing": ["Invoices", "Solar savings, budget pace, and grid charges"]
};

const mobileNav = [
  { to: "/", label: "Live", icon: Gauge },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/devices", label: "Devices", icon: Zap },
  { to: "/billing", label: "Billing", icon: ReceiptText }
];

export function Topbar() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const [title, subtitle] = titles[location.pathname] ?? ["VoltStream", "Energy intelligence console"];

  return (
    <header className="sticky top-4 z-20">
      <div className="glass flex min-h-20 items-center justify-between rounded-[8px] px-4 py-3 sm:px-5">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-cyan-200">
            <Activity className="h-3.5 w-3.5" />
            Live telemetry
          </div>
          <h1 className="mt-1 truncate text-xl font-semibold text-white sm:text-2xl">{title}</h1>
          <p className="hidden truncate text-sm text-slate-400 sm:block">{subtitle}</p>
        </div>
        <button
          aria-label="Open navigation"
          onClick={() => setOpen((value) => !value)}
          className="grid h-10 w-10 place-items-center rounded-[8px] border border-white/10 bg-white/5 text-white lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>
      </div>

      {open ? (
        <motion.nav
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass mt-3 grid grid-cols-2 gap-2 rounded-[8px] p-2 lg:hidden"
        >
          {mobileNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-[8px] px-3 py-3 text-sm ${
                  isActive ? "bg-cyan-300/10 text-cyan-100" : "text-slate-300"
                }`
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </motion.nav>
      ) : null}
    </header>
  );
}
