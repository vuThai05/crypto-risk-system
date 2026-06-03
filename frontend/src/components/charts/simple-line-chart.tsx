import { toNumber } from "@/lib/format";

type Series = {
  label: string;
  color: string;
  values: Array<{ x: string; y: string | number | null }>;
};

type SimpleLineChartProps = {
  series?: Series[];
  data?: Array<Record<string, string | number>>;
  dataKeys?: string[];
  title?: string;
  subtitle?: string;
  yMax?: number;
  height?: number;
};

const palette = ["#0f766e", "#2563eb", "#d97706", "#e11d48", "#8b5cf6", "#64748b"];

export function SimpleLineChart({
  series,
  data,
  dataKeys,
  title,
  subtitle,
  yMax = 100,
  height = 260,
}: SimpleLineChartProps) {
  const resolvedSeries =
    series ??
    (dataKeys ?? []).map((key, index) => ({
      label: key,
      color: palette[index % palette.length],
      values: (data ?? []).map((point) => ({
        x: String(point.date ?? ""),
        y: point[key] as string | number | null,
      })),
    }));

  const width = 720;
  const left = 42;
  const right = 20;
  const top = 14;
  const bottom = 28;
  const innerWidth = width - left - right;
  const innerHeight = height - top - bottom;
  const values = resolvedSeries.flatMap((item) =>
    item.values.map((point) => toNumber(point.y)).filter((value): value is number => value !== null),
  );
  const maxY = yMax ?? Math.max(1, ...values);
  const minY = 0;
  const range = maxY - minY || 1;
  const ticks = [0, 0.25, 0.5, 0.75, 1];

  const pointFor = (item: Series, index: number) => {
    const yValue = toNumber(item.values[index]?.y);
    if (yValue === null) return null;
    const x = left + (index / Math.max(item.values.length - 1, 1)) * innerWidth;
    const y = top + innerHeight - ((yValue - minY) / range) * innerHeight;
    return { x, y };
  };

  const linePath = (item: Series) =>
    item.values
      .map((_, index) => {
        const point = pointFor(item, index);
        return point ? `${index === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}` : "";
      })
      .filter(Boolean)
      .join(" ");

  const chart =
    values.length === 0 ? (
      <div className="flex h-64 items-center justify-center rounded-lg bg-slate-50 text-sm text-slate-500">
        No chart data available
      </div>
    ) : (
      <div className="overflow-x-auto">
        <svg className="min-w-[580px]" role="img" aria-label="Risk score line chart" viewBox={`0 0 ${width} ${height}`}>
          {ticks.map((tick) => {
            const y = top + tick * innerHeight;
            const label = Math.round(maxY - tick * range);
            return (
              <g key={tick}>
                <line x1={left} x2={left + innerWidth} y1={y} y2={y} stroke="#e2e8f0" strokeWidth="1" />
                <text x={left - 7} y={y + 4} textAnchor="end" fontSize="10" fill="#94a3b8" fontWeight="600">
                  {label}
                </text>
              </g>
            );
          })}
          {resolvedSeries.map((item, index) => (
            <path
              key={index}
              d={linePath(item)}
              fill="none"
              stroke={item.color}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2.5"
            />
          ))}
        </svg>
        <div className="mt-4 flex flex-wrap gap-4">
          {resolvedSeries.map((item) => (
            <div className="flex items-center gap-2" key={item.label}>
              <span className="block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="text-xs font-medium text-slate-500">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    );

  if (!title) return chart;

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-console">
      <div className="mb-6">
        <h2 className="text-base font-semibold text-slate-950">{title}</h2>
        {subtitle ? <p className="mt-2 text-sm text-slate-500">{subtitle}</p> : null}
      </div>
      {chart}
    </section>
  );
}
