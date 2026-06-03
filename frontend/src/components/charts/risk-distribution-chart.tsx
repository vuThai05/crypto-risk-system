import { AlertTriangle } from "lucide-react";

import { HorizontalBarList } from "@/components/charts/horizontal-bar-list";
import type { MarketOverviewAsset } from "@/lib/types";

type DistributionRow = { risk_level: string; count: number };

export function RiskDistributionChart({
  data,
  distribution,
  compact = false,
}: {
  data?: MarketOverviewAsset[];
  distribution?: DistributionRow[];
  compact?: boolean;
}) {
  const levels = ["Low", "Medium", "High", "Extreme", "Unknown"];
  const colors: Record<string, string> = {
    Low: "#10b981",
    Medium: "#f59e0b",
    High: "#ef4444",
    Extreme: "#8b5cf6",
    Unknown: "#cbd5e1"
  };
  const rows = levels.map((level) => ({
    label: level,
    value: distribution?.find((item) => item.risk_level === level)?.count ?? data?.filter((asset) => (asset.risk_level || "Unknown") === level).length ?? 0,
    color: colors[level]
  }));

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-console">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-950">Risk Distribution</h2>
          <p className="mt-1 text-sm text-slate-500">{compact ? "Latest asset count by risk level" : "Asset count by risk band"}</p>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-md bg-amber-50 text-amber-600">
          <AlertTriangle className="h-4 w-4" aria-hidden="true" />
        </div>
      </div>
      <HorizontalBarList rows={rows} />
    </section>
  );
}
