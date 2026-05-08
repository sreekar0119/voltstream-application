import { NavLink } from "react-router-dom";
import { BarChart3, BatteryCharging, Gauge, ReceiptText, Zap } from "lucide-react";

const navItems = [
  { to: "/", label: "Live Grid", icon: Gauge },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/devices", label: "Devices", icon: Zap },
  { to: "/billing", label: "Billing", icon: ReceiptText }
];

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-white/10 bg-slate-950/58 p-4 backdrop-blur-2xl lg:block">
      <div className="flex h-full flex-col">
        <div className="flex items-center gap-3 px-2 py-3">
          <div className="energy-glow grid h-11 w-11 place-items-center rounded-[8px] bg-cyan-300/10">
            <BatteryCharging className="h-6 w-6 text-cyan-200" />
          </div>
          <div>
            <p className="text-lg font-semibold text-white">VoltStream</p>
            <p className="text-xs text-slate-400">Prosumer OS</p>
          </div>
        </div>

        <nav className="mt-8 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `group flex items-center gap-3 rounded-[8px] px-3 py-3 text-sm transition ${
                  isActive
                    ? "bg-cyan-300/10 text-cyan-100 ring-1 ring-cyan-300/20"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              <item.icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  );
}
