import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Cpu, PlugZap, ShieldCheck, Zap } from "lucide-react";
import { api } from "../services/api.js";
import { useApi } from "../hooks/useApi.js";
import { pageMotion } from "../animations/variants.js";
import { AlertBanner } from "../components/AlertBanner.jsx";
import { ChartCard } from "../components/ChartCard.jsx";
import { DeviceCard } from "../components/DeviceCard.jsx";
import { LoadingDashboard } from "../components/LoadingState.jsx";
import { MetricCard } from "../components/MetricCard.jsx";
import { DeviceCategoryChart } from "../charts/DeviceCategoryChart.jsx";
import { number } from "../utils/format.js";

export function SmartControl() {
  const { data, error, loading, refresh } = useApi(api.devices, []);
  const [category, setCategory] = useState("All");
  const [busy, setBusy] = useState(null);

  const categories = useMemo(() => ["All", ...new Set((data ?? []).map((device) => device.category))], [data]);
  const visible = useMemo(
    () => (data ?? []).filter((device) => category === "All" || device.category === category),
    [data, category]
  );

  async function toggleDevice(id, status) {
    setBusy(id);
    try {
      await api.updateDevice(id, status);
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  if (loading) return <LoadingDashboard />;
  if (error) return <AlertBanner tone="rose">{error}</AlertBanner>;

  const active = data.filter((device) => device.status === "on");
  const activeLoad = active.reduce((sum, device) => sum + device.power_usage, 0);
  const healthy = data.filter((device) => device.health === "optimal").length;

  return (
    <motion.div {...pageMotion} className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Online devices" value={active.length} unit={`of ${data.length}`} change={0} icon={PlugZap} tone="cyan" />
        <MetricCard label="Active load" value={activeLoad / 1000} unit="kW" change={2.4} icon={Zap} tone="blue" />
        <MetricCard label="Healthy systems" value={healthy} unit="optimal" change={1} icon={ShieldCheck} tone="green" />
        <MetricCard label="Categories" value={categories.length - 1} unit="zones" change={0} icon={Cpu} tone="amber" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[.75fr_1.25fr]">
        <ChartCard title="Load by category" subtitle="Circuit allocation across smart home systems">
          <DeviceCategoryChart devices={data} />
          <p className="mt-3 text-center text-sm text-slate-400">{number(activeLoad)} W currently active</p>
        </ChartCard>
        <section className="glass rounded-[8px] p-4 sm:p-5">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-semibold text-white">Smart appliance command</h2>
              <p className="mt-1 text-sm text-slate-400">Toggle devices and monitor health state by category.</p>
            </div>
            <div className="flex max-w-full gap-2 overflow-x-auto rounded-[8px] p-1 custom-scrollbar">
              {categories.map((item) => (
                <button
                  key={item}
                  onClick={() => setCategory(item)}
                  className={`shrink-0 rounded-[8px] px-3 py-2 text-sm transition ${
                    category === item ? "bg-cyan-300/10 text-cyan-100" : "bg-white/5 text-slate-400 hover:text-white"
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {visible.map((device) => (
              <DeviceCard key={device.id} device={device} busy={busy === device.id} onToggle={toggleDevice} />
            ))}
          </div>
        </section>
      </div>
    </motion.div>
  );
}
