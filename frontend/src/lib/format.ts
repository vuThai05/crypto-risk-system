export function toNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const numberValue = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numberValue) ? numberValue : null;
}

export function formatScore(value: unknown) {
  const numberValue = toNumber(value);
  return numberValue === null ? "N/A" : numberValue.toFixed(1);
}

export function formatPercent(value: unknown) {
  const numberValue = toNumber(value);
  if (numberValue === null) return "N/A";
  const sign = numberValue > 0 ? "+" : "";
  return `${sign}${numberValue.toFixed(2)}%`;
}

export function formatMoney(value: unknown) {
  const numberValue = toNumber(value);
  if (numberValue === null) return "N/A";

  if (Math.abs(numberValue) >= 1_000_000_000_000) {
    return `$${(numberValue / 1_000_000_000_000).toFixed(2)}T`;
  }
  if (Math.abs(numberValue) >= 1_000_000_000) {
    return `$${(numberValue / 1_000_000_000).toFixed(2)}B`;
  }
  if (Math.abs(numberValue) >= 1_000_000) {
    return `$${(numberValue / 1_000_000).toFixed(2)}M`;
  }
  if (Math.abs(numberValue) >= 1) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 2
    }).format(numberValue);
  }
  return `$${numberValue.toFixed(4)}`;
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) return "N/A";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}
