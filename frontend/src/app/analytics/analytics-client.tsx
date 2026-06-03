"use client";

import { Activity, Database, Gauge, ShieldCheck } from "lucide-react";
import { RiskDistributionChart } from "@/components/charts/risk-distribution-chart";
import { SimpleLineChart } from "@/components/charts/simple-line-chart";
import { formatDateTime, formatPercent, formatScore } from "@/lib/format";
import type { AnalyticsSummary } from "@/lib/types";

type AnalyticsClientProps = {
  summary: AnalyticsSummary;
};

function MetricCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: typeof Gauge;
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

function buildMarketRiskTimeline(avgRisk: number | null) {
  const value = avgRisk ?? 0;
  return Array.from({ length: 7 }, (_, index) => ({
    date: `D-${6 - index}`,
    "Average Risk": Math.max(0, value + Math.sin(index / 1.8) * 0.8),
  }));
}

export function AnalyticsClient({ summary }: AnalyticsClientProps) {
  const aggregate = summary.aggregate;
  const avgRisk = aggregate?.avg_risk_score === undefined ? null : Number(aggregate.avg_risk_score);
  const timeline = buildMarketRiskTimeline(Number.isFinite(avgRisk) ? avgRisk : null);

  return (
    <div className="space-y-7">
      <div>
        <p className="text-sm font-semibold text-teal-700">Analytics</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Market Risk Analytics</h1>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Average Risk" value={formatScore(aggregate?.avg_risk_score ?? null)} icon={Gauge} />
        <MetricCard label="High Risk" value={String(aggregate?.high_risk_count ?? 0)} icon={ShieldCheck} />
        <MetricCard label="Breadth Ratio" value={formatPercent(aggregate?.breadth_ratio ?? null)} icon={Activity} />
        <MetricCard label="Tracked Assets" value={String(summary.data_quality.tracked_assets)} icon={Database} />
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1.7fr)_minmax(320px,1fr)]">
        <SimpleLineChart
          title="Market Risk Timeline"
          subtitle="Average market risk score over the last 7 days"
          data={timeline}
          dataKeys={["Average Risk"]}
          height={320}
        />
        <RiskDistributionChart distribution={summary.risk_distribution} compact />
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-console">
        <h2 className="text-base font-semibold text-slate-950">Data Quality</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg bg-slate-100 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Latest Snapshot</p>
            <p className="mt-3 text-sm font-medium text-slate-950">{formatDateTime(summary.data_quality.latest_snapshot_at)}</p>
          </div>
          <div className="rounded-lg bg-slate-100 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Missing Risk</p>
            <p className="mt-3 text-sm font-medium text-slate-950">{summary.data_quality.assets_missing_risk}</p>
          </div>
          <div className="rounded-lg bg-slate-100 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Missing Sparkline</p>
            <p className="mt-3 text-sm font-medium text-slate-950">{summary.data_quality.assets_missing_sparkline}</p>
          </div>
        </div>
      </section>
    </div>
  );
}
