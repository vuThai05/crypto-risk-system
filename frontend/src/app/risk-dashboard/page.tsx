import { AppShell } from "@/components/layout/app-shell";
import { getAnalyticsSummary, getMarketOverview } from "@/services/risk-dashboard-service";
import { RiskDashboardClient } from "./risk-dashboard-client";

export default async function RiskDashboardPage() {
  const [summary, assets] = await Promise.all([
    getAnalyticsSummary(),
    getMarketOverview(100).catch(() => []),
  ]);

  return (
    <AppShell>
      <RiskDashboardClient summary={summary} assets={assets} />
    </AppShell>
  );
}
