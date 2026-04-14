# 04_STATE.md

Use this prompt to design Phase 1 frontend state. This file assumes `01_TECH_STACK.md` and `03_API.md` have already been read.

## Prompt

You are a senior frontend engineer defining state management for the Crypto Risk System Phase 1 UI.

Project context:
- Main experience: a risk bubble map for top-100 coins.
- Supporting experiences: coin risk dossier, market weather, and data trust/ops.
- Backend updates market/risk data on a scheduled worker, with market ingestion every 15 minutes, OHLCV every 12 hours, and backfill every 7 days.
- Frontend API reads must be cacheable and should not create noisy polling.
- Data can be stale; freshness must be represented in state.

## State Principles

- Server state belongs in TanStack Query.
- UI state belongs in local component state unless it is shared across major regions.
- Use Zustand only for shared UI state that needs to survive page boundaries or coordinate multiple components.
- Derived state should be computed from cached server data, not stored separately.
- Do not duplicate the same data in TanStack Query and Zustand.

## Server State

Use these query keys:

```ts
["riskMap"]
["marketWeather"]
["coinDossier", coinId]
["dataFreshness"]
```

Use this mutation key:

```ts
["triggerIngestion"]
```

Suggested cache behavior:
- `riskMap`: `staleTime` 60-120 seconds, `refetchInterval` 120-300 seconds.
- `marketWeather`: same cadence as `riskMap`.
- `coinDossier`: `staleTime` 60-120 seconds, refetch when selected coin changes.
- `dataFreshness`: `staleTime` 30-60 seconds, `refetchInterval` 60-120 seconds.
- `triggerIngestion`: invalidate all risk-related queries on success.

Do not refetch on every keystroke in search/filter controls. Fetch the top-100 risk map once and filter locally.

## Global UI State

Create a small store such as `useRiskMapStore` for:

```ts
type RiskMapFilters = {
  query: string;
  rankMin: number;
  rankMax: number;
  riskLevels: Array<"Low" | "Medium" | "High" | "Extreme">;
  sizeBy: "market_cap" | "risk_score";
  colorBy: "risk_level" | "percent_change_24h";
};

type RiskMapUiState = {
  filters: RiskMapFilters;
  selectedCoinId: string | null;
  isInsightRailOpen: boolean;
  isFilterRailOpen: boolean;
};
```

Keep these local, not global:
- Hovered bubble.
- Tooltip position.
- Canvas dimensions.
- Force simulation internal nodes.
- Form input draft values that do not affect other components.

## Derived State

Compute these from `riskMap` data:
- Filtered coins.
- Risk level counts.
- Top extreme coins.
- Bubble radius scale.
- Bubble color scale.
- Stale warning copy.
- Market summary labels.

Compute these from `coinDossier` data:
- Risk DNA contribution display.
- Latest usable feature window.
- Data trust summary for the selected coin.

## URL State

Use URL search params only for shareable filters:
- `q`
- `rank`
- `levels`
- `coin`

Do not store hover state or panel animation state in the URL.

## Loading, Empty, And Error State

Every query-consuming component must handle:
- Initial loading.
- Background refetch.
- Empty data.
- Stale data.
- Request error.
- Partial missing fields, especially `market_cap`, `image_url`, and feature metrics.

For empty data:
- Show a clear setup path: start worker or trigger ingestion.
- Do not show fake risk numbers unless the page is explicitly using mock data.

For stale data:
- Keep the last successful result visible.
- Add a freshness warning.
- Do not clear the bubble map just because a refetch failed.

## Output Required From The Agent

When this prompt is used, output:
- TanStack Query hooks to create.
- Zustand store shape and actions, if needed.
- Derived selectors.
- Loading/empty/error state behavior.
- Which state should be URL-driven.

## Acceptance Criteria

- The bubble map remains stable while filters change.
- Typing in search does not spam the backend.
- Manual ingestion refresh invalidates the correct data.
- Stale data stays visible with a warning.
- Components do not carry backend-specific table concerns.
