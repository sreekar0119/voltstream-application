import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { shortMonth } from "../utils/format.js";

export function BillingChart({ data, height = 300 }) {
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
          <CartesianGrid stroke="rgba(148,163,184,.1)" vertical={false} />
          <XAxis dataKey="month" tickFormatter={shortMonth} tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip
            cursor={{ fill: "rgba(94,234,212,.08)" }}
            contentStyle={{
              background: "rgba(2,6,23,.94)",
              border: "1px solid rgba(148,163,184,.2)",
              borderRadius: 8,
              color: "#e2e8f0"
            }}
          />
          <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
          <Bar dataKey="bill_amount" name="Bill" fill="#60a5fa" radius={[4, 4, 0, 0]} />
          <Bar dataKey="solar_savings" name="Solar savings" fill="#5eead4" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
