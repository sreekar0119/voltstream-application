import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { compactDate } from "../utils/format.js";

export function EnergyAreaChart({ data, height = 320 }) {
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ left: 0, right: 16, top: 12, bottom: 0 }}>
          <defs>
            <linearGradient id="solarGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#5eead4" stopOpacity={0.55} />
              <stop offset="100%" stopColor="#5eead4" stopOpacity={0.03} />
            </linearGradient>
            <linearGradient id="usageGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#60a5fa" stopOpacity={0.44} />
              <stop offset="100%" stopColor="#60a5fa" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(148,163,184,.12)" vertical={false} />
          <XAxis
            dataKey="timestamp"
            tickFormatter={compactDate}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            minTickGap={34}
          />
          <YAxis
            domain={[0, "dataMax + 1"]}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              background: "rgba(2,6,23,.94)",
              border: "1px solid rgba(148,163,184,.2)",
              borderRadius: 8,
              color: "#e2e8f0"
            }}
            labelFormatter={(value) => compactDate(value)}
          />
          <Area
            type="monotone"
            dataKey="solar_generation"
            name="Solar"
            stroke="#5eead4"
            strokeWidth={3}
            fill="url(#solarGradient)"
            fillOpacity={1}
            animationDuration={900}
            activeDot={{ r: 6, stroke: "#ecfeff", strokeWidth: 3 }}
          />
          <Area
            type="monotone"
            dataKey="energy_usage"
            name="Usage"
            stroke="#60a5fa"
            strokeWidth={3}
            fill="url(#usageGradient)"
            fillOpacity={1}
            animationDuration={1100}
            activeDot={{ r: 6, stroke: "#eff6ff", strokeWidth: 3 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
