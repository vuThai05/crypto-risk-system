import { AppShell } from "@/components/layout/app-shell";
import { getMarketOverview } from "@/services/risk-dashboard-service";
import { MarketsClient } from "./markets-client";

export default async function MarketsPage() {
  const assets = await getMarketOverview(100).catch(() => []);

  return (
    <AppShell>
      <div className="space-y-7">
        <div>
          <p className="text-sm font-semibold text-teal-700">Markets</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Market Overview</h1>
        </div>
        <MarketsClient assets={assets} />
      </div>
    </AppShell>
  );
}
