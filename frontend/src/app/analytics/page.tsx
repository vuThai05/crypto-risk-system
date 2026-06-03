import { AppShell } from "@/components/layout/app-shell";
import { getAnalyticsSummary } from "@/services/risk-dashboard-service";
import { AnalyticsClient } from "./analytics-client";

export default async function AnalyticsPage() {
  const summary = await getAnalyticsSummary();

  return (
    <AppShell>
      <AnalyticsClient summary={summary} />
    </AppShell>
  );
}
