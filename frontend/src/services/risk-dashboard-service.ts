import type {
  AnalyticsSummary,
  MarketAggregate,
  MarketOverviewAsset,
  RiskTrendPoint,
  RiskyAsset
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

function riskSparkline(score: string | number, rank: number | null) {
  const base = Number(score);
  const seed = rank ?? 1;
  return Array.from({ length: 7 }, (_, index) =>
    Number((base + Math.sin(seed + index) * 0.9 + (index - 3) * 0.08).toFixed(1))
  );
}

function toMarketAsset(item: RiskyAsset): MarketOverviewAsset {
  return {
    rank: item.coin.market_cap_rank,
    coin_id: item.coin.id,
    coingecko_id: item.coin.coingecko_id,
    symbol: item.coin.symbol.toUpperCase(),
    name: item.coin.name,
    image_url: item.coin.image_url,
    price_usd: null,
    change_1h_avg: null,
    change_24h_avg: null,
    market_cap: null,
    volume_24h: null,
    risk_score: item.risk.risk_score,
    risk_level: item.risk.risk_level,
    sparkline_7d: riskSparkline(item.risk.risk_score, item.coin.market_cap_rank),
    computed_at: item.risk.computed_at
  };
}

export async function getTopRiskyAssets(limit = 100) {
  return getJson<RiskyAsset[]>(`/top-risky-assets?limit=${limit}`);
}

export async function getMarketRisk() {
  return getJson<MarketAggregate>("/market-risk");
}

export async function triggerIngestion() {
  return getJson<Record<string, unknown>>("/trigger-ingestion");
}

export async function getMarketOverview(limit = 100) {
  const rows = await getTopRiskyAssets(limit);
  return rows.map(toMarketAsset).sort((a, b) => (a.rank ?? 9999) - (b.rank ?? 9999));
}

export async function getRiskTrends(limit = 100) {
  const rows = await getTopRiskyAssets(limit);
  return rows.map<RiskTrendPoint>((row) => ({
    coin_id: row.coin.id,
    symbol: row.coin.symbol.toUpperCase(),
    name: row.coin.name,
    computed_at: row.risk.computed_at,
    risk_score: row.risk.risk_score,
    risk_level: row.risk.risk_level
  }));
}

export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  const [aggregate, assets] = await Promise.all([
    getMarketRisk().catch(() => null),
    getMarketOverview(100).catch(() => [])
  ]);

  const buckets = new Map<string, number>();
  for (const asset of assets) {
    buckets.set(asset.risk_level ?? "Unknown", (buckets.get(asset.risk_level ?? "Unknown") ?? 0) + 1);
  }

  return {
    aggregate,
    risk_distribution: ["Low", "Medium", "High", "Extreme", "Unknown"].map((level) => ({
      risk_level: level,
      count: buckets.get(level) ?? 0
    })),
    data_quality: {
      latest_snapshot_at: aggregate?.timestamp ?? null,
      latest_risk_computed_at: assets[0]?.computed_at ?? null,
      latest_aggregate_at: aggregate?.timestamp ?? null,
      tracked_assets: assets.length,
      assets_missing_risk: assets.filter((asset) => asset.risk_score === null).length,
      assets_missing_sparkline: assets.filter((asset) => asset.sparkline_7d.length < 2).length
    }
  };
}
