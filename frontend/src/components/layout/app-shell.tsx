import type { ReactNode } from "react";

import { TopNav } from "@/components/layout/top-nav";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <TopNav />
      <main className="mx-auto w-full max-w-[1296px] px-4 py-6 sm:px-6">{children}</main>
    </div>
  );
}
