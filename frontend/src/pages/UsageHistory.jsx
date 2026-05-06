import { useCallback, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Activity, CloudSun, Thermometer, Zap } from "lucide-react";
import { api } from "../services/api.js";
import { useApi } from "../hooks/useApi.js";
import { pageMotion } from "../animations/variants.js";
import { AlertBanner } from "../components/AlertBanner.jsx";
import { ChartCard } from "../components/ChartCard.jsx";
import { LoadingDashboard } from "../components/LoadingState.jsx";
import { MetricCard } from "../components/MetricCard.jsx";
import { CostChart } from "../charts/CostChart.jsx";
import { EnergyAreaChart } from "../charts/EnergyAreaChart.jsx";
import { GridDrawChart } from "../charts/GridDrawChart.jsx";
import { currency, number } from "../utils/format.js";

export function UsageHistory() {
  const [range, setRange] = useState("Weekly");
  const period = range.toLowerCase();
  const loadAnalytics = useCallback(() => api.analyticsHistory(period), [period]);
  const { data, error, loading } = useApi(loadAnalytics);

  const records = useMemo(() => data ?? [], [data]);
  const totals = useMemo(() => {
    const usage = records.reduce((sum, item) => sum + item.energy_usage, 0);
    const solar = records.reduce((sum, item) => sum + item.solar_generation, 0);
    const cost = records.reduce((sum, item) => sum + item.cost, 0);
    const temp = records.reduce((sum, item) => sum + item.temperature, 0) / Math.max(1, records.length);
    return { usage, solar, cost, temp };
  }, [records]);

  if (loading) return <LoadingDashboard />;
  if (error) return <AlertBanner tone="rose">{error}</AlertBanner>;

  return (
    <motion.div {...pageMotion} className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Usage" value={totals.usage} unit="kWh" change={3.2} icon={Zap} tone="blue" />
          <MetricCard label="Solar" value={totals.solar} unit="kWh" change={5.8} icon={CloudSun} tone="cyan" />
          <MetricCard label="Grid cost" value={currency(totals.cost)} unit="" change={-2.1} icon={Activity} tone="amber" />
          <MetricCard label="Avg temp" value={totals.temp} unit="F" change={1.4} icon={Thermometer} tone="green" />
        </div>
        <div className="glass-soft flex rounded-[8px] p-1">
          {["Daily", "Weekly", "Monthly"].map((item) => (
            <button
              key={item}
              onClick={() => setRange(item)}
              className={`rounded-[8px] px-4 py-2 text-sm transition ${range === item ? "bg-cyan-300/10 text-cyan-100" : "text-slate-400 hover:text-white"}`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      <ChartCard title={`${range} load curve`} subtitle="Solar generation and home energy usage, sampled hourly">
        <EnergyAreaChart data={records} height={360} />
      </ChartCard>

      <div className="grid gap-5 xl:grid-cols-2">
        <ChartCard title="Grid draw intensity" subtitle="When the home imports power from the utility">
          <GridDrawChart data={records} />
        </ChartCard>
        <ChartCard title="Electricity cost curve" subtitle="Hourly cost impact after solar contribution">
          <CostChart data={records} />
        </ChartCard>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Insight label="Peak usage" value={`${number(Math.max(...records.map((r) => r.energy_usage)))} kW`} />
        <Insight label="Peak solar" value={`${number(Math.max(...records.map((r) => r.solar_generation)))} kW`} />
        <Insight label="Voltage band" value={`${number(Math.min(...records.map((r) => r.voltage)))}-${number(Math.max(...records.map((r) => r.voltage)))} V`} />
      </div>
    </motion.div>
  );
}

function Insight({ label, value }) {
  return (
    <div className="glass-soft rounded-[8px] p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    </div>
  );
}
