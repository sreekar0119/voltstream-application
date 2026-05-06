import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { compactDate } from "../utils/format.js";

export function GridDrawChart({ data, height = 260 }) {
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
          <CartesianGrid stroke="rgba(148,163,184,.1)" vertical={false} />
          <XAxis
            dataKey="timestamp"
            tickFormatter={compactDate}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            minTickGap={40}
          />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip
            cursor={{ fill: "rgba(34,211,238,.08)" }}
            contentStyle={{
              background: "rgba(2,6,23,.94)",
              border: "1px solid rgba(148,163,184,.2)",
              borderRadius: 8,
              color: "#e2e8f0"
            }}
            labelFormatter={(value) => compactDate(value)}
          />
          <Bar dataKey="grid_draw" name="Grid draw" fill="#22d3ee" radius={[4, 4, 0, 0]} animationDuration={900} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
