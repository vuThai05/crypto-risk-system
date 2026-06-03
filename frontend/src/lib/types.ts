export type RiskLevel = "Low" | "Medium" | "High" | "Extreme" | "Unknown" | string;

export type CoinPublic = {
  id: string;
  coingecko_id: string;
  symbol: string;
  name: string;
  market_cap_rank: number | null;
  image_url: string | null;
};

export type RiskMetricPublic = {
  id: string;
  coin_id: string;
  risk_score: string | number;
  risk_level: RiskLevel;
  model_version: string;
  config_hash: string;
  computed_at: string;
};

export type MarketSnapshotPublic = {
  id: string;
  coin_id: string;
  price_usd: string | number;
  market_cap: string | number | null;
  volume_24h: string | number | null;
  percent_change_1h: string | number | null;
  percent_change_24h: string | number | null;
  percent_change_7d: string | number | null;
  timestamp: string;
};

export type RiskyAsset = {
  coin: CoinPublic;
  risk: RiskMetricPublic;
  snapshot?: MarketSnapshotPublic | null;
};

export type MarketAggregate = {
  id: string;
  avg_risk_score: string | number;
  high_risk_count: number;
  extreme_risk_count: number;
  breadth_ratio: string | number | null;
  market_volatility: string | number | null;
  btc_dominance: string | number | null;
  timestamp: string;
};

export type MarketOverviewAsset = {
  rank: number | null;
  coin_id: string;
  coingecko_id: string;
  symbol: string;
  name: string;
  image_url: string | null;
  price_usd: string | number | null;
  change_1h_avg: string | number | null;
  change_24h_avg: string | number | null;
  market_cap: string | number | null;
  volume_24h: string | number | null;
  risk_score: string | number | null;
  risk_level: RiskLevel;
  sparkline_7d: Array<string | number>;
  computed_at?: string;
};

export type RiskTrendPoint = {
  coin_id: string;
  symbol: string;
  name: string;
  computed_at: string;
  risk_score: string | number;
  risk_level: RiskLevel;
};

export type AnalyticsSummary = {
  aggregate: MarketAggregate | null;
  risk_distribution: Array<{ risk_level: RiskLevel; count: number }>;
  data_quality: {
    latest_snapshot_at: string | null;
    latest_risk_computed_at: string | null;
    latest_aggregate_at: string | null;
    tracked_assets: number;
    assets_missing_risk: number;
    assets_missing_sparkline: number;
  };
};
