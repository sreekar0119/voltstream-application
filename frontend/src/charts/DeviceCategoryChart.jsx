import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const colors = ["#22d3ee", "#5eead4", "#bef264", "#60a5fa", "#facc15", "#c084fc"];

export function DeviceCategoryChart({ devices, height = 260 }) {
  const groups = devices.reduce((acc, device) => {
    const current = acc.get(device.category) ?? 0;
    acc.set(device.category, current + device.power_usage);
    return acc;
  }, new Map());
  const data = Array.from(groups, ([name, value]) => ({ name, value }));

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius="54%" outerRadius="82%" paddingAngle={3} animationDuration={900}>
            {data.map((entry, index) => (
              <Cell key={entry.name} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "rgba(2,6,23,.94)",
              border: "1px solid rgba(148,163,184,.2)",
              borderRadius: 8,
              color: "#e2e8f0"
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
