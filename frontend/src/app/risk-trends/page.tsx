import { AppShell } from "@/components/layout/app-shell";
import { getMarketOverview, getRiskTrends } from "@/services/risk-dashboard-service";
import { RiskTrendsClient } from "./risk-trends-client";

export default async function RiskTrendsPage() {
  const [assets, trendPoints] = await Promise.all([
    getMarketOverview(100).catch(() => []),
    getRiskTrends(100).catch(() => []),
  ]);

  return (
    <AppShell>
      <RiskTrendsClient assets={assets} trendPoints={trendPoints} />
    </AppShell>
  );
}
