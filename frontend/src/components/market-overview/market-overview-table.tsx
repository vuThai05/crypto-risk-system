"use client";

import Image from "next/image";
import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  useReactTable
} from "@tanstack/react-table";
import { ArrowUpDown, RefreshCw, Search, Star, AlertTriangle } from "lucide-react";
import { useMemo, useState } from "react";

import { RiskLevelBadge } from "@/components/market-overview/risk-level-badge";
import { Sparkline } from "@/components/market-overview/sparkline";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useWatchlist } from "@/hooks/use-watchlist";
import { formatMoney, formatScore, toNumber } from "@/lib/format";
import type { MarketOverviewAsset } from "@/lib/types";
import { cn } from "@/lib/utils";

type Props = {
  data: MarketOverviewAsset[];
  isLoading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
};

function SortButton({ label, onClick }: { label: string; onClick?: () => void }) {
  return (
    <button className="inline-flex items-center gap-1 text-xs font-semibold uppercase text-slate-500 hover:text-slate-950" onClick={onClick} type="button">
      {label}
      <ArrowUpDown className="h-3 w-3" aria-hidden="true" />
    </button>
  );
}

function PercentChange({ value }: { value: unknown }) {
  const numeric = toNumber(value);
  if (numeric === null) return <span className="text-slate-500">N/A</span>;
  return <span className={numeric >= 0 ? "text-emerald-700" : "text-rose-600"}>{numeric >= 0 ? "+" : ""}{numeric.toFixed(2)}%</span>;
}

export function MarketOverviewTable({ data, isLoading = false, error = null, onRefresh }: Props) {
  const [sorting, setSorting] = useState<SortingState>([{ id: "rank", desc: false }]);
  const [searchQuery, setSearchQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");
  const [watchlistOnly, setWatchlistOnly] = useState(false);
  const { isWatchlisted, toggleWatchlist } = useWatchlist();

  const filteredData = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    return data.filter((asset) => {
      const matchesSearch = !query || asset.name.toLowerCase().includes(query) || asset.symbol.toLowerCase().includes(query);
      const matchesRisk = riskFilter === "All" || asset.risk_level === riskFilter;
      const matchesWatchlist = !watchlistOnly || isWatchlisted(asset.coin_id);
      return matchesSearch && matchesRisk && matchesWatchlist;
    });
  }, [data, isWatchlisted, riskFilter, searchQuery, watchlistOnly]);

  const columns = useMemo<ColumnDef<MarketOverviewAsset>[]>(
    () => [
      {
        id: "watchlist",
        header: "",
        cell: ({ row }) => {
          const active = isWatchlisted(row.original.coin_id);
          return (
            <button
              aria-label={active ? `Remove ${row.original.name} from watchlist` : `Add ${row.original.name} to watchlist`}
              className={cn("flex h-8 w-8 items-center justify-center rounded-md transition-colors", active ? "bg-amber-50 text-amber-500" : "text-slate-300 hover:bg-slate-50 hover:text-amber-500")}
              onClick={() => toggleWatchlist(row.original.coin_id)}
              type="button"
            >
              <Star className={cn("h-4 w-4", active && "fill-current")} aria-hidden="true" />
            </button>
          );
        }
      },
      {
        accessorKey: "rank",
        header: ({ column }) => <SortButton label="#" onClick={() => column.toggleSorting()} />,
        cell: ({ row }) => <span className="text-sm tabular-nums text-slate-500">{row.original.rank ?? "N/A"}</span>
      },
      {
        accessorKey: "name",
        header: ({ column }) => <SortButton label="Asset" onClick={() => column.toggleSorting()} />,
        cell: ({ row }) => (
          <div className="flex min-w-44 items-center gap-3">
            {row.original.image_url ? (
              <Image alt="" className="rounded-full" height={28} src={row.original.image_url} width={28} />
            ) : (
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-500">
                {row.original.symbol.slice(0, 2)}
              </div>
            )}
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold text-slate-950">{row.original.name}</div>
              <div className="text-xs uppercase text-slate-500">{row.original.symbol}</div>
            </div>
          </div>
        )
      },
      { accessorKey: "price_usd", header: ({ column }) => <SortButton label="Price" onClick={() => column.toggleSorting()} />, cell: ({ row }) => <span className="font-medium tabular-nums">{formatMoney(row.original.price_usd)}</span> },
      { accessorKey: "change_1h_avg", header: ({ column }) => <SortButton label="1H" onClick={() => column.toggleSorting()} />, cell: ({ row }) => <PercentChange value={row.original.change_1h_avg} /> },
      { accessorKey: "change_24h_avg", header: ({ column }) => <SortButton label="24H" onClick={() => column.toggleSorting()} />, cell: ({ row }) => <PercentChange value={row.original.change_24h_avg} /> },
      { accessorKey: "market_cap", header: ({ column }) => <SortButton label="Market Cap" onClick={() => column.toggleSorting()} />, cell: ({ row }) => <span className="tabular-nums text-slate-700">{formatMoney(row.original.market_cap)}</span> },
      { accessorKey: "volume_24h", header: ({ column }) => <SortButton label="Volume" onClick={() => column.toggleSorting()} />, cell: ({ row }) => <span className="tabular-nums text-slate-700">{formatMoney(row.original.volume_24h)}</span> },
      {
        accessorKey: "risk_score",
        header: ({ column }) => <SortButton label="Risk" onClick={() => column.toggleSorting()} />,
        cell: ({ row }) => (
          <div className="flex min-w-[110px] items-center gap-2">
            <RiskLevelBadge level={row.original.risk_level} />
            <span className="text-sm font-semibold tabular-nums">{formatScore(row.original.risk_score)}</span>
          </div>
        )
      },
      { id: "sparkline", header: () => <span className="text-xs font-semibold uppercase text-slate-500">7D</span>, cell: ({ row }) => <Sparkline values={row.original.sparkline_7d} /> }
    ],
    [isWatchlisted, toggleWatchlist]
  );

  const table = useReactTable({ data: filteredData, columns, state: { sorting }, onSortingChange: setSorting, getCoreRowModel: getCoreRowModel(), getSortedRowModel: getSortedRowModel() });

  return (
    <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-console">
      <div className="flex flex-col gap-4 border-b border-slate-100 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-950">Tracked Crypto Assets</h2>
          <p className="mt-2 text-sm text-slate-500">{filteredData.length} of {data.length} assets</p>
        </div>
        <Button disabled={isLoading} onClick={onRefresh ?? (() => window.location.reload())} size="sm" type="button" variant="outline">
          <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} aria-hidden="true" />
          Refresh
        </Button>
      </div>
      {error ? (
        <div className="mx-6 mt-5 flex items-center gap-2 rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          <AlertTriangle className="h-4 w-4" aria-hidden="true" />
          {error}
        </div>
      ) : null}
      <div className="flex flex-col gap-3 border-b border-slate-100 px-6 py-4 lg:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          <input className="h-10 w-full rounded-md border border-slate-200 bg-white pl-10 pr-4 text-sm outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-700/10" onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search coin or symbol" value={searchQuery} />
        </div>
        <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-700/10" onChange={(event) => setRiskFilter(event.target.value)} value={riskFilter}>
          <option value="All">All risk levels</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Extreme">Extreme</option>
        </select>
        <button className={cn("flex h-10 items-center justify-center gap-2 rounded-md border px-4 text-sm font-medium", watchlistOnly ? "border-amber-200 bg-amber-50 text-amber-700" : "border-slate-200 bg-white text-slate-700")} onClick={() => setWatchlistOnly(!watchlistOnly)} type="button">
          <Star className={cn("h-4 w-4", watchlistOnly && "fill-current text-amber-500")} aria-hidden="true" />
          Watchlist only
        </button>
      </div>
      <div className="overflow-x-auto">
        <Table className="min-w-[1120px]">
          <TableHeader className="bg-slate-50/70">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow className="hover:bg-transparent" key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>{header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}</TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>)}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </section>
  );
}
