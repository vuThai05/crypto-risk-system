import { cn } from "@/lib/utils";

type Row = {
  label: string;
  value: number;
  color?: string;
};

type HorizontalBarListProps = {
  rows?: Row[];
  items?: Row[];
  title?: string;
  subtitle?: string;
  footer?: string;
  maxValue?: number;
  valueFormatter?: (value: number) => string;
  iconTone?: string;
  emptyLabel?: string;
};

export function HorizontalBarList({
  rows,
  items,
  title,
  subtitle,
  footer,
  maxValue,
  valueFormatter,
  emptyLabel = "No data available",
}: HorizontalBarListProps) {
  const resolvedRows = rows ?? items ?? [];
  const resolvedMaxValue = maxValue ?? Math.max(1, ...resolvedRows.map((row) => row.value));
  const colorFor = (color?: string) => {
    if (color === "rose") return "#e11d48";
    if (color === "amber") return "#d97706";
    if (color === "teal") return "#0f766e";
    return color;
  };

  if (resolvedRows.length === 0) {
    return <div className="rounded-lg bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">{emptyLabel}</div>;
  }

  const content = (
    <div className="space-y-4">
      {resolvedRows.map((row) => (
        <div className="grid grid-cols-[88px_1fr_48px] items-center gap-3" key={row.label}>
          <div className="truncate text-sm font-semibold text-slate-950">{row.label}</div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className={cn("h-full rounded-full", !row.color && "bg-teal-700")}
              style={{
                width: `${Math.max(3, (row.value / resolvedMaxValue) * 100)}%`,
                backgroundColor: colorFor(row.color),
              }}
            />
          </div>
          <div className="text-right text-sm font-semibold tabular-nums text-slate-950">
            {valueFormatter ? valueFormatter(row.value) : row.value.toFixed(1)}
          </div>
        </div>
      ))}
    </div>
  );

  if (!title) return content;

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-console">
      <div className="mb-6">
        <h2 className="text-base font-semibold text-slate-950">{title}</h2>
        {subtitle ? <p className="mt-2 text-sm text-slate-500">{subtitle}</p> : null}
      </div>
      {content}
      {footer ? <p className="mt-5 text-xs text-slate-500">{footer}</p> : null}
    </section>
  );
}
