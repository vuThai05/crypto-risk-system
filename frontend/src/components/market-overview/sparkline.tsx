import { toNumber } from "@/lib/format";

export function Sparkline({ values }: { values: Array<number | string> }) {
  const points = values.map(toNumber).filter((value): value is number => value !== null);
  if (points.length < 2) return <div className="h-8 w-28 rounded-md bg-slate-100" aria-hidden="true" />;

  const width = 120;
  const height = 36;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const path = points
    .map((value, index) => {
      const x = (index / (points.length - 1)) * width;
      const y = height - ((value - min) / range) * (height - 4) - 2;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
  const positive = points[points.length - 1] >= points[0];
  const stroke = positive ? "#10b981" : "#ef4444";

  return (
    <svg className="h-9 w-[120px] overflow-visible" role="img" aria-label="7 day trend" viewBox={`0 0 ${width} ${height}`}>
      <path d={path} fill="none" stroke={stroke} strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
    </svg>
  );
}
