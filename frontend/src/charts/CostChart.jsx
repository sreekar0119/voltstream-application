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

export function CostChart({ data, height = 260 }) {
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
          <defs>
            <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#facc15" stopOpacity={0.42} />
              <stop offset="100%" stopColor="#facc15" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(148,163,184,.1)" vertical={false} />
          <XAxis
            dataKey="timestamp"
            tickFormatter={compactDate}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            minTickGap={42}
          />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
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
            dataKey="cost"
            name="Cost"
            stroke="#facc15"
            strokeWidth={2.4}
            fill="url(#costGradient)"
            animationDuration={1000}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
