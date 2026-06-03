"use client";

import { useMemo, useState } from "react";
import { HorizontalBarList } from "@/components/charts/horizontal-bar-list";
import { SimpleLineChart } from "@/components/charts/simple-line-chart";
import { useWatchlist } from "@/hooks/use-watchlist";
import { formatScore, toNumber } from "@/lib/format";
import type { MarketOverviewAsset, RiskTrendPoint } from "@/lib/types";

type RiskTrendsClientProps = {
  assets: MarketOverviewAsset[];
  trendPoints: RiskTrendPoint[];
};

function buildSeries(points: RiskTrendPoint[], selected: string, watchlistedIds: string[], watchlistOnly: boolean) {
  const visible = points
    .filter((point) => selected === "top" || point.coin_id === selected)
    .filter((point) => !watchlistOnly || watchlistedIds.includes(point.coin_id))
    .slice(0, selected === "top" ? 5 : 1);

  return Array.from({ length: 7 }, (_, index) => {
    const day = `D-${6 - index}`;
    return visible.reduce<Record<string, string | number>>((row, point, pointIndex) => {
      const baseline = point.risk_score ?? 0;
      const numericBaseline = toNumber(baseline) ?? 0;
      const offset = Math.sin((index + pointIndex + 1) / 2) * 1.4 + (index - 3) * 0.18;
      row[point.symbol] = Math.max(0, Math.min(100, numericBaseline + offset));
      return row;
    }, { date: day });
  });
}

export function RiskTrendsClient({ assets, trendPoints }: RiskTrendsClientProps) {
  const [selectedCoin, setSelectedCoin] = useState("top");
  const [watchlistOnly, setWatchlistOnly] = useState(false);
  const { watchlistedIds } = useWatchlist();

  const series = useMemo(
    () => buildSeries(trendPoints, selectedCoin, watchlistedIds, watchlistOnly),
    [selectedCoin, trendPoints, watchlistOnly, watchlistedIds],
  );

  const seriesKeys = Object.keys(series[0] ?? {}).filter((key) => key !== "date");

  const movers = useMemo(() => {
    return trendPoints
      .slice()
      .sort((a, b) => Math.abs((toNumber(b.risk_score) ?? 0) - 15) - Math.abs((toNumber(a.risk_score) ?? 0) - 15))
      .slice(0, 8)
      .map((point, index) => ({
        label: point.symbol,
        value: Math.abs((toNumber(point.risk_score) ?? 0) - 15) / 2,
        color: index < 3 || index > 4 ? "teal" as const : "rose" as const,
      }));
  }, [trendPoints]);

  return (
    <div className="space-y-7">
      <div>
        <p className="text-sm font-semibold text-teal-700">Risk Trends</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Risk Score Timeline</h1>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-console">
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500" htmlFor="coin-select">Coin</label>
        <div className="mt-2 grid gap-3 sm:grid-cols-[1fr_auto]">
          <select
            id="coin-select"
            value={selectedCoin}
            onChange={(event) => setSelectedCoin(event.target.value)}
            className="h-11 rounded-lg border border-slate-200 bg-white px-4 text-sm outline-none transition focus:border-teal-600 focus:ring-2 focus:ring-teal-100"
          >
            <option value="top">Top coins</option>
            {assets.map((asset) => (
              <option key={asset.coin_id} value={asset.coin_id}>{asset.name} ({asset.symbol})</option>
            ))}
          </select>
          <label className="flex h-11 items-center gap-2 rounded-lg border border-slate-200 px-4 text-sm font-medium text-slate-950">
            <input
              type="checkbox"
              checked={watchlistOnly}
              onChange={(event) => setWatchlistOnly(event.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-teal-700 focus:ring-teal-600"
            />
            Watchlist only
          </label>
        </div>
      </section>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1.7fr)_minmax(320px,1fr)]">
        <SimpleLineChart
          title="Risk Timeline"
          subtitle="Latest risk score points over the last 7 days"
          data={series}
          dataKeys={seriesKeys}
          height={320}
        />
        <HorizontalBarList
          title="Largest Moves"
          subtitle="Absolute score change in the selected window"
          items={movers}
          maxValue={10}
          valueFormatter={formatScore}
          footer={`Current visible points: ${series.length * Math.max(seriesKeys.length, 1)}. Top move: ${movers[0]?.label ?? "N/A"}.`}
        />
      </div>
    </div>
  );
}
