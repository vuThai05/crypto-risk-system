import { MarketOverviewTable } from "@/components/market-overview/market-overview-table";
import type { MarketOverviewAsset } from "@/lib/types";

type MarketsClientProps = {
  assets: MarketOverviewAsset[];
};

export function MarketsClient({ assets }: MarketsClientProps) {
  return <MarketOverviewTable data={assets} />;
}
