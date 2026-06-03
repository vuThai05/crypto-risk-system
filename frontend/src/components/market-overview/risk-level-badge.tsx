import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const styles: Record<string, string> = {
  Low: "border-emerald-200 bg-emerald-50 text-emerald-700",
  Medium: "border-amber-200 bg-amber-50 text-amber-700",
  High: "border-rose-200 bg-rose-50 text-rose-700",
  Extreme: "border-purple-200 bg-purple-50 text-purple-700",
  Unknown: "border-slate-200 bg-slate-50 text-slate-600"
};

export function RiskLevelBadge({ level }: { level: string | null | undefined }) {
  const value = level || "Unknown";
  return <Badge className={cn("min-w-16 justify-center", styles[value] ?? styles.Unknown)}>{value}</Badge>;
}
