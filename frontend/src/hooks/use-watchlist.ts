"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

const WATCHLIST_STORAGE_KEY = "crypto-risk-watchlist:v1";

function readWatchlist() {
  if (typeof window === "undefined") return [];
  try {
    const rawValue = window.localStorage.getItem(WATCHLIST_STORAGE_KEY);
    const parsed = rawValue ? JSON.parse(rawValue) : [];
    return Array.isArray(parsed) ? parsed.filter((value): value is string => typeof value === "string") : [];
  } catch {
    return [];
  }
}

export function useWatchlist() {
  const [watchlistedIds, setWatchlistedIds] = useState<string[]>([]);

  useEffect(() => {
    setWatchlistedIds(readWatchlist());
  }, []);

  const persist = useCallback((nextIds: string[]) => {
    setWatchlistedIds(nextIds);
    window.localStorage.setItem(WATCHLIST_STORAGE_KEY, JSON.stringify(nextIds));
  }, []);

  const watchlistedSet = useMemo(() => new Set(watchlistedIds), [watchlistedIds]);
  const isWatchlisted = useCallback((coinId: string) => watchlistedSet.has(coinId), [watchlistedSet]);
  const toggleWatchlist = useCallback(
    (coinId: string) => {
      persist(watchlistedSet.has(coinId) ? watchlistedIds.filter((id) => id !== coinId) : [...watchlistedIds, coinId]);
    },
    [persist, watchlistedIds, watchlistedSet]
  );

  return { watchlistedIds, isWatchlisted, toggleWatchlist };
}
