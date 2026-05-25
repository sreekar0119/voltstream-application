import { useEffect } from "react";
import { motion } from "framer-motion";
import { CloudSun, Cpu, IndianRupee, Leaf, PlugZap, Zap } from "lucide-react";
import { api } from "../services/api.js";
import { useApi } from "../hooks/useApi.js";
import { pageMotion, stagger } from "../animations/variants.js";
import { AlertBanner } from "../components/AlertBanner.jsx";
import { ChartCard } from "../components/ChartCard.jsx";
import { EnergyGauge } from "../components/EnergyGauge.jsx";
import { GlassPanel } from "../components/GlassPanel.jsx";
import { LoadingDashboard } from "../components/LoadingState.jsx";
import { MetricCard } from "../components/MetricCard.jsx";
import { ProgressBar } from "../components/ProgressBar.jsx";
import { EnergyAreaChart } from "../charts/EnergyAreaChart.jsx";
import { currency, number } from "../utils/format.js";

const icons = [CloudSun, PlugZap, Cpu, IndianRupee];

export function LiveDashboard() {
  const dashboard = useApi(api.liveDashboard, []);
  const analytics = useApi(api.analyticsHistory, []);
  const refreshDashboard = dashboard.refresh;

  useEffect(() => {
    const id = window.setInterval(() => {
      refreshDashboard({ silent: true });
    }, 10000);
    window.addEventListener("voltstream:devices-updated", refreshDashboard);

    return () => {
      window.clearInterval(id);
      window.removeEventListener("voltstream:devices-updated", refreshDashboard);
    };
  }, [refreshDashboard]);

  if (dashboard.loading || analytics.loading) return <LoadingDashboard />;

  if (dashboard.error || analytics.error) {
    return <AlertBanner tone="rose">{dashboard.error || analytics.error}</AlertBanner>;
  }

  const live = dashboard.data;
  const recent = analytics.data.slice(-36);

  function exportPdf() {
    window.print();
  }

  return (
    <div data-export-root="true" className="print-root space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-cyan-200">Live dashboard snapshot</p>
          <h1 className="mt-2 text-2xl font-semibold text-white">VoltStream Energy Overview</h1>
        </div>
        <button
          type="button"
          data-no-export="true"
          onClick={exportPdf}
          className="no-print rounded-[8px] border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:border-cyan-200/30 hover:bg-cyan-300/10"
        >
          Download PDF
        </button>
      </div>

      <motion.div {...pageMotion} className="space-y-6">
        <motion.div variants={stagger} initial="initial" animate="animate" className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {live.metrics.map((metric, index) => (
          <MetricCard key={metric.label} {...metric} icon={icons[index]} showChange />
        ))}
        </motion.div>

        <div className="grid gap-5 xl:grid-cols-[1.25fr_.75fr]">
          <GlassPanel className="overflow-hidden p-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-medium uppercase tracking-[0.18em] text-cyan-200">Whole-home energy flow</p>
                <h2 className="mt-2 text-2xl font-semibold text-white">Solar-first orchestration</h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                  Battery gateway is balancing generation, grid draw, and active circuit demand in real time.
                </p>
              </div>
              <div className="rounded-[8px] border border-emerald-300/20 bg-emerald-300/10 px-3 py-2 text-sm text-emerald-100">
                {live.budget_status}
              </div>
            </div>

            <div className="mt-8 grid gap-5 lg:grid-cols-3">
              <EnergyGauge value={live.battery_storage_percent} label="Battery storage" tone="green" />
              <div className="glass-soft rounded-[8px] p-5 lg:col-span-2">
                <div className="grid gap-4 sm:grid-cols-3">
                  <EnergyNode icon={CloudSun} label="Solar" value={`${number(live.solar_generation)} kW`} tone="cyan" />
                  <EnergyNode icon={Zap} label="Net load" value={`${number(live.net_energy_usage)} kW`} tone="blue" />
                  <EnergyNode icon={Leaf} label="Offset today" value={`${number(live.carbon_offset_today)} lb`} tone="green" />
                </div>
                <div className="mt-8">
                  <div className="mb-3 flex justify-between text-sm">
                    <span className="text-slate-400">Monthly budget pace</span>
                    <span className="font-medium text-white">{number(live.budget_used_percent)}%</span>
                  </div>
                  <ProgressBar value={live.budget_used_percent} tone={live.budget_used_percent > 100 ? "rose" : "cyan"} />
                </div>
                <div className="mt-8 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-[8px] border border-white/10 bg-white/5 p-4">
                    <p className="text-sm text-slate-400">Projected monthly cost</p>
                    <p className="mt-2 text-2xl font-semibold text-white">{currency(live.projected_energy_cost)}</p>
                  </div>
                  <div className="rounded-[8px] border border-white/10 bg-white/5 p-4">
                    <p className="text-sm text-slate-400">Home efficiency score</p>
                    <p className="mt-2 text-2xl font-semibold text-white">{live.home_efficiency_score}/100</p>
                  </div>
                </div>
              </div>
            </div>
          </GlassPanel>

          <GlassPanel className="p-5">
            <h2 className="text-base font-semibold text-white">Live circuit status</h2>
            <div className="mt-5 space-y-4">
              <StatusRow label="Active devices" value={`${live.active_devices}/${live.total_devices}`} />
              <StatusRow label="Current grid draw" value={`${number(live.current_grid_draw)} kW`} />
              <StatusRow label="Solar contribution" value={`${number(Math.max(0, live.solar_generation - live.current_grid_draw))} kW`} />
              <StatusRow label="Battery reserve" value={`${number(live.battery_storage_percent)}%`} />
            </div>
          </GlassPanel>
        </div>

        <ChartCard title="36-hour energy telemetry" subtitle="Usage, solar generation, and storage behavior from the analytics dataset">
          <EnergyAreaChart data={recent} height={310} />
          <div className="grid gap-3 sm:grid-cols-3">
            {recent.slice(-3).map((point) => (
              <div key={point.id} className="rounded-[8px] border border-white/10 bg-white/5 p-3">
                <p className="text-xs text-slate-500">{new Date(point.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</p>
                <p className="mt-1 text-sm text-slate-300">
                  {number(point.energy_usage)} kW used - {number(point.solar_generation)} kW solar
                </p>
              </div>
            ))}
          </div>
        </ChartCard>
      </motion.div>
    </div>
  );
}

function EnergyNode({ icon: Icon, label, value, tone }) {
  const color = tone === "green" ? "text-emerald-200 bg-emerald-300/10" : tone === "blue" ? "text-blue-100 bg-blue-300/10" : "text-cyan-100 bg-cyan-300/10";
  return (
    <div className="rounded-[8px] border border-white/10 bg-white/5 p-4">
      <div className={`grid h-10 w-10 place-items-center rounded-[8px] ${color}`}>
        <Icon className="h-5 w-5" />
      </div>
      <p className="mt-4 text-sm text-slate-400">{label}</p>
      <p className="mt-1 text-xl font-semibold text-white">{value}</p>
    </div>
  );
}

function StatusRow({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-white/10 pb-3 last:border-0">
      <span className="text-sm text-slate-400">{label}</span>
      <span className="font-semibold text-white">{value}</span>
    </div>
  );
}
