import { FileSearch, Sparkles } from "lucide-react";

const tabs = [
  { id: "energy", label: "Energy AI", icon: Sparkles },
  { id: "qa", label: "PDF Q&A", icon: FileSearch }
];

export function AssistantTabs({ activeTab, onChange }) {
  return (
    <div className="grid grid-cols-2 gap-2 rounded-[8px] border border-white/10 bg-slate-950/40 p-1">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const active = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={`flex h-10 items-center justify-center gap-2 rounded-[8px] text-sm font-medium transition ${
              active
                ? "bg-cyan-300/15 text-cyan-100 shadow-[0_0_22px_rgba(34,211,238,0.16)]"
                : "text-slate-400 hover:bg-white/5 hover:text-slate-100"
            }`}
          >
            <Icon className="h-4 w-4" />
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
