import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Cpu, Plus, PlugZap, ShieldCheck, X, Zap } from "lucide-react";
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
  const [showForm, setShowForm] = useState(false);
  const [formError, setFormError] = useState("");
  const [deviceForm, setDeviceForm] = useState({
    name: "",
    category: "Utility",
    room: "General",
    status: "off",
    power_usage: 0,
    health: "optimal",
    daily_active_hours: 0
  });

  const categories = useMemo(() => ["All", ...new Set((data ?? []).map((device) => device.category))], [data]);
  const visible = useMemo(
    () => (data ?? []).filter((device) => category === "All" || device.category === category),
    [data, category]
  );

  useEffect(() => {
    window.addEventListener("voltstream:devices-updated", refresh);
    return () => window.removeEventListener("voltstream:devices-updated", refresh);
  }, [refresh]);

  async function toggleDevice(id, status) {
    setBusy(id);
    try {
      await api.updateDevice(id, status);
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  async function submitDevice(event) {
    event.preventDefault();
    setBusy("new-device");
    setFormError("");
    try {
      await api.addDevice({
        ...deviceForm,
        power_usage: Number(deviceForm.power_usage),
        daily_active_hours: Number(deviceForm.daily_active_hours)
      });
      setDeviceForm({
        name: "",
        category: "Utility",
        room: "General",
        status: "off",
        power_usage: 0,
        health: "optimal",
        daily_active_hours: 0
      });
      setShowForm(false);
      await refresh();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setBusy(null);
    }
  }

  async function removeDevice(id) {
    setBusy(id);
    try {
      await api.deleteDevice(id);
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  function updateForm(field, value) {
    setDeviceForm((current) => ({ ...current, [field]: value }));
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
          <div className="flex min-h-0 items-center justify-center">
            <div className="w-full max-w-[360px]">
              <DeviceCategoryChart devices={data} />
            </div>
          </div>
          <p className="mt-3 text-center text-sm text-slate-400">{number(activeLoad)} W currently active</p>
        </ChartCard>
        <section className="glass rounded-[8px] p-4 sm:p-5">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-semibold text-white">Smart appliance command</h2>
              <p className="mt-1 text-sm text-slate-400">Toggle devices and monitor health state by category.</p>
            </div>
            <div className="flex max-w-full flex-wrap items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowForm((value) => !value)}
                className="inline-flex h-10 items-center gap-2 rounded-[8px] bg-cyan-300 px-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
              >
                {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                Add Device
              </button>
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
          </div>
          {showForm && (
            <form onSubmit={submitDevice} className="mb-5 grid gap-3 rounded-[8px] border border-white/10 bg-slate-950/35 p-4 md:grid-cols-4">
              <input
                required
                minLength={2}
                maxLength={80}
                value={deviceForm.name}
                onChange={(event) => updateForm("name", event.target.value)}
                placeholder="Device name"
                className="h-11 rounded-[8px] border border-white/10 bg-slate-950/60 px-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
              />
              <input
                required
                minLength={2}
                maxLength={40}
                value={deviceForm.category}
                onChange={(event) => updateForm("category", event.target.value)}
                placeholder="Category"
                className="h-11 rounded-[8px] border border-white/10 bg-slate-950/60 px-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
              />
              <input
                required
                minLength={2}
                maxLength={40}
                value={deviceForm.room}
                onChange={(event) => updateForm("room", event.target.value)}
                placeholder="Room"
                className="h-11 rounded-[8px] border border-white/10 bg-slate-950/60 px-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
              />
              <input
                required
                type="number"
                min="0"
                max="20000"
                value={deviceForm.power_usage}
                onChange={(event) => updateForm("power_usage", event.target.value)}
                placeholder="Watts"
                className="h-11 rounded-[8px] border border-white/10 bg-slate-950/60 px-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
              />
              <select
                value={deviceForm.status}
                onChange={(event) => updateForm("status", event.target.value)}
                className="h-11 rounded-[8px] border border-white/10 bg-slate-950/60 px-3 text-sm text-white outline-none transition focus:border-cyan-300/60"
              >
                <option value="off">Off</option>
                <option value="on">On</option>
              </select>
              <select
                value={deviceForm.health}
                onChange={(event) => updateForm("health", event.target.value)}
                className="h-11 rounded-[8px] border border-white/10 bg-slate-950/60 px-3 text-sm text-white outline-none transition focus:border-cyan-300/60"
              >
                <option value="optimal">Optimal</option>
                <option value="attention">Attention</option>
                <option value="idle">Idle</option>
                <option value="offline">Offline</option>
              </select>
              <input
                required
                type="number"
                min="0"
                max="24"
                step="0.1"
                value={deviceForm.daily_active_hours}
                onChange={(event) => updateForm("daily_active_hours", event.target.value)}
                placeholder="Daily hours"
                className="h-11 rounded-[8px] border border-white/10 bg-slate-950/60 px-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
              />
              {formError && <p className="text-sm text-rose-200 md:col-span-3">{formError}</p>}
              <button
                type="submit"
                disabled={busy === "new-device"}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-[8px] bg-cyan-300 px-4 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:opacity-60 md:col-start-4"
              >
                <Plus className="h-4 w-4" />
                Save Device
              </button>
            </form>
          )}
          <div className="max-h-[60vh] overflow-x-auto overflow-y-auto custom-scrollbar pr-2">
            <div className="grid min-w-[680px] gap-4 md:grid-cols-2">
              {visible.map((device) => (
                <DeviceCard
                  key={device.id}
                  device={device}
                  busy={busy === device.id}
                  onToggle={toggleDevice}
                  onDelete={removeDevice}
                />
              ))}
            </div>
          </div>
        </section>
      </div>
    </motion.div>
  );
}
