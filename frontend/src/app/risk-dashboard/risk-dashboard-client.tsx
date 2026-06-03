"use client";

import Link from "next/link";
import { AlertTriangle, Database, ShieldCheck, TrendingUp } from "lucide-react";
import { HorizontalBarList } from "@/components/charts/horizontal-bar-list";
import { RiskDistributionChart } from "@/components/charts/risk-distribution-chart";
import { formatMoney, formatScore, toNumber } from "@/lib/format";
import type { AnalyticsSummary, MarketOverviewAsset } from "@/lib/types";

type RiskDashboardClientProps = {
  summary: AnalyticsSummary;
  assets: MarketOverviewAsset[];
};

function MetricCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: typeof Database;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-console">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
          <p className="mt-3 text-2xl font-semibold tracking-tight text-slate-950">{value}</p>
        </div>
        <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-slate-100 text-teal-700">
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}

export function RiskDashboardClient({ summary, assets }: RiskDashboardClientProps) {
  const aggregate = summary.aggregate;
  const topAssets = assets
    .slice()
    .sort((a, b) => (toNumber(b.risk_score) ?? 0) - (toNumber(a.risk_score) ?? 0))
    .slice(0, 8);

  return (
    <div className="space-y-7">
      <div>
        <p className="text-sm font-semibold text-teal-700">Market Risk Console</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Risk Dashboard</h1>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Assets" value={String(summary.data_quality.tracked_assets)} icon={Database} />
        <MetricCard label="Market Cap" value={formatMoney(null)} icon={TrendingUp} />
        <MetricCard label="Average Risk" value={formatScore(aggregate?.avg_risk_score ?? null)} icon={ShieldCheck} />
        <MetricCard label="High Risk" value={String(aggregate?.high_risk_count ?? 0)} icon={AlertTriangle} />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <RiskDistributionChart distribution={summary.risk_distribution} />
        <HorizontalBarList
          title="Top Risk Assets"
          subtitle="Highest latest risk scores"
          items={topAssets.map((asset) => ({
            label: asset.symbol,
            value: toNumber(asset.risk_score) ?? 0,
            color: "rose",
          }))}
          maxValue={100}
          valueFormatter={(value) => formatScore(value)}
          iconTone="rose"
        />
      </div>

      <section className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white px-6 py-5 shadow-console sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">Market Table</h2>
          <p className="mt-2 text-sm text-slate-500">Full sorting, filtering, search, and watchlist controls live on Markets.</p>
        </div>
        <Link
          className="inline-flex h-10 items-center justify-center rounded-md bg-teal-700 px-4 text-sm font-semibold text-white transition-colors hover:bg-teal-800"
          href="/markets"
        >
          Open Markets
        </Link>
      </section>
    </div>
  );
}
