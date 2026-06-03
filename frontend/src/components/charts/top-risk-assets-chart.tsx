import { ShieldAlert } from "lucide-react";

import { HorizontalBarList } from "@/components/charts/horizontal-bar-list";
import { toNumber } from "@/lib/format";
import type { MarketOverviewAsset } from "@/lib/types";

export function TopRiskAssetsChart({ data }: { data: MarketOverviewAsset[] }) {
  const rows = [...data]
    .filter((asset) => toNumber(asset.risk_score) !== null)
    .sort((a, b) => (toNumber(b.risk_score) ?? 0) - (toNumber(a.risk_score) ?? 0))
    .slice(0, 8)
    .map((asset) => ({ label: asset.symbol, value: toNumber(asset.risk_score) ?? 0, color: "#e11d48" }));

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-console">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-950">Top Risk Assets</h2>
          <p className="mt-1 text-sm text-slate-500">Highest latest risk scores</p>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-md bg-rose-50 text-rose-600">
          <ShieldAlert className="h-4 w-4" aria-hidden="true" />
        </div>
      </div>
      <HorizontalBarList rows={rows} emptyLabel="No risk scores available" />
    </section>
  );
}
