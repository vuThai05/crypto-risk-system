"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Gauge, LineChart, Table2 } from "lucide-react";

import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", href: "/risk-dashboard", icon: Gauge },
  { label: "Markets", href: "/markets", icon: Table2 },
  { label: "Risk Trends", href: "/risk-trends", icon: LineChart },
  { label: "Analytics", href: "/analytics", icon: BarChart3 }
];

export function TopNav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/95 backdrop-blur">
      <div className="mx-auto flex min-h-[72px] w-full max-w-[1296px] flex-col gap-3 px-4 py-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-teal-700 text-white shadow-sm shadow-teal-700/20">
            <Gauge className="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <div className="text-sm font-semibold tracking-tight text-slate-950">Crypto Risk</div>
            <div className="text-xs font-medium text-slate-500">System Console</div>
          </div>
        </div>
        <nav className="flex gap-1.5 overflow-x-auto pb-1 lg:pb-0">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                className={cn(
                  "flex h-9 shrink-0 items-center gap-2 rounded-lg border px-3.5 text-sm font-medium transition-colors",
                  active
                    ? "border-teal-50 bg-teal-50 text-teal-800"
                    : "border-transparent text-slate-600 hover:bg-slate-50 hover:text-slate-950"
                )}
                href={item.href}
                key={item.href}
              >
                <Icon className={cn("h-4 w-4", active ? "text-teal-700" : "text-slate-500")} aria-hidden="true" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
