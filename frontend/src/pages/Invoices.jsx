import { motion } from "framer-motion";
import { Banknote, Leaf, TrendingDown, WalletCards } from "lucide-react";
import { api } from "../services/api.js";
import { useApi } from "../hooks/useApi.js";
import { pageMotion } from "../animations/variants.js";
import { AlertBanner } from "../components/AlertBanner.jsx";
import { ChartCard } from "../components/ChartCard.jsx";
import { LoadingDashboard } from "../components/LoadingState.jsx";
import { MetricCard } from "../components/MetricCard.jsx";
import { ProgressBar } from "../components/ProgressBar.jsx";
import { BillingChart } from "../charts/BillingChart.jsx";
import { currency, number } from "../utils/format.js";

export function Invoices() {
  const { data, error, loading } = useApi(api.billingSummary, []);

  if (loading) return <LoadingDashboard />;
  if (error) return <AlertBanner tone="rose">{error}</AlertBanner>;

  const latest = data.latest;

  return (
    <motion.div {...pageMotion} className="space-y-5">
      {data.budget_exceeded ? (
        <AlertBanner tone="amber">Projected usage is ahead of budget. Shift heavy loads to solar peak windows.</AlertBanner>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Latest bill" value={currency(latest.bill_amount)} unit="" change={data.bill_trend_percent} icon={WalletCards} tone="blue" />
        <MetricCard label="Annual spend" value={currency(data.annual_spend)} unit="" change={-4.2} icon={Banknote} tone="amber" />
        <MetricCard label="Solar savings" value={currency(data.annual_savings)} unit="" change={8.6} icon={TrendingDown} tone="cyan" />
        <MetricCard label="Carbon offset" value={data.total_carbon_offset} unit="lb" change={5.4} icon={Leaf} tone="green" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.25fr_.75fr]">
        <ChartCard title="12-month billing intelligence" subtitle="Monthly invoice amount compared against realized solar savings">
          <BillingChart data={data.records} />
        </ChartCard>

        <section className="glass rounded-[8px] p-5">
          <h2 className="text-base font-semibold text-white">Budget command center</h2>
          <div className="mt-5 rounded-[8px] border border-white/10 bg-white/5 p-4">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Budget used</span>
              <span className="font-medium text-white">{number(data.budget_used_percent)}%</span>
            </div>
            <div className="mt-3">
              <ProgressBar value={data.budget_used_percent} tone={data.budget_used_percent > 100 ? "rose" : "cyan"} />
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <BillStat label="Budget" value={currency(latest.budget)} />
              <BillStat label="Charges" value={currency(latest.grid_charges)} />
              <BillStat label="Service" value={currency(latest.service_fees)} />
              <BillStat label="Usage" value={`${number(latest.usage_kwh, 0)} kWh`} />
            </div>
          </div>
          <div className="mt-4 rounded-[8px] border border-emerald-300/20 bg-emerald-300/10 p-4">
            <p className="text-sm font-medium text-emerald-100">Solar ROI signal</p>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              This home has avoided {currency(data.annual_savings)} in grid spend across the trailing 12 months.
            </p>
          </div>
        </section>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {data.records.slice(-4).map((record) => (
          <article key={record.id} className="glass-soft rounded-[8px] p-4">
            <div className="flex items-center justify-between gap-2">
              <h3 className="font-semibold text-white">{record.month}</h3>
              <span className="rounded-full bg-cyan-300/10 px-2.5 py-1 text-xs text-cyan-100">{number(record.carbon_offset)} lb CO2</span>
            </div>
            <p className="mt-4 text-3xl font-semibold text-white">{currency(record.bill_amount)}</p>
            <p className="mt-2 text-sm text-slate-400">{currency(record.solar_savings)} solar savings</p>
          </article>
        ))}
      </div>
    </motion.div>
  );
}

function BillStat({ label, value }) {
  return (
    <div className="rounded-[8px] border border-white/10 bg-slate-950/30 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-white">{value}</p>
    </div>
  );
}
