# 05_COMPONENT.md

Use this prompt to define the Phase 1 component system. This file intentionally does not define the final visual style; `02_DESIGN.md` will own colors, typography, and motion.

## Prompt

You are a senior frontend engineer designing the component inventory for the Crypto Risk System Phase 1 UI.

Project context:
- The product is a crypto market risk intelligence tool, not a price-prediction dashboard.
- The primary Phase 1 interaction is an interactive top-100 risk bubble map.
- Users should be able to see market risk, inspect a coin, understand why the risk score exists, and verify data freshness.
- Current backend endpoints are narrow, so components should be designed against the Phase 1 API contracts from `03_API.md`.

## Component Principles

- The bubble map is the hero experience, not a decorative chart.
- Avoid generic KPI-card grids as the primary surface.
- Components must support loading, empty, error, stale, and partial-data states.
- Keep repeated item components small and stable.
- Do not put cards inside cards.
- Use real coin images from backend `image_url` where available; provide a symbol fallback.
- UI copy should speak in risk language, not trading advice.

## Required Components

### App And Layout

`AppShell`
- Owns top-level route outlet and global providers.
- Does not fetch risk data directly.

`TopCommandBar`
- Contains product label, search, rank filter summary, refresh action, and data status badge.
- Fixed height around 56-64px.

`FilterRail`
- Contains risk-level toggles, rank range, size mode, color mode.
- Desktop: persistent left rail.
- Tablet/mobile: collapsible drawer or sheet.

`InsightRail`
- Contains market weather, top extreme coins, freshness summary, and selected coin summary.
- Desktop: persistent right rail.
- Tablet/mobile: collapsible drawer.

`BottomStatusStrip`
- Shows latest ingestion/risk freshness, model version, and stale warnings.
- Compact and stable.

### Bubble Experience

`RiskBubbleCanvas`
- Canvas-based top-100 bubble board.
- Uses `d3-force` for collision/positioning.
- Receives normalized bubble data and UI callbacks.
- Must support hover, click, keyboard fallback list access, resize, and stable animation.

`BubbleTooltip`
- Shows symbol, name, risk score, risk level, 24h change, and last updated.
- Position is local UI state.

`RiskLegend`
- Explains risk colors and optional price-change ring/glow.
- Small, persistent, and non-blocking.

`BubbleEmptyState`
- Used when no risk map data exists.
- Should tell the user to start the worker or trigger ingestion.

### Market Risk

`MarketWeatherStrip`
- Shows market state, avg risk score, high risk count, extreme count, and freshness.
- Uses `GET /market-weather`.

`MarketRiskSummary`
- Shows breadth ratio, market volatility, and BTC dominance.
- This is supportive, not the page hero.

`ExtremeCoinList`
- Shows a compact list of highest-risk coins from the risk map response.
- Clicking a row selects the coin and opens the dossier.

### Coin Dossier

`CoinDossierPanel`
- Opens when a bubble or list item is selected.
- Can become a full page later via `/coins/:coinId`.
- Uses `GET /coins/{coin_id}/risk-dossier`.

`CoinIdentityHeader`
- Shows coin image/symbol/name/rank and current risk level.

`RiskScoreBlock`
- Shows score and level clearly, with timestamp.

`RiskDNA`
- Shows volatility, drawdown, and average return as explainable contributors.
- Do not imply financial advice or prediction.

`FeatureMetricRow`
- Displays one feature window such as `7d` or `30d`.

`DataTrustBlock`
- Shows freshness status, model version, config hash, and computed timestamp.

### Ops And Feedback

`DataFreshnessPanel`
- Uses `GET /system/data-freshness`.
- Shows fresh/lagging/stale/empty/error state.

`TriggerIngestionButton`
- Uses `POST /trigger-ingestion`.
- Shows pending, success, and failure states.
- Invalidates relevant queries after success.

`PipelineStatusStepper`
- Shows `CoinGecko -> ingestion -> features -> risk -> aggregates -> UI`.
- For Phase 1, it can use freshness timestamps rather than a full job-run table.

`QueryStateBoundary`
- Reusable wrapper for loading/error/empty/stale state where helpful.
- Do not hide stale data if last successful data exists.

## Output Required From The Agent

When this prompt is used, output:
- Component inventory grouped by domain.
- Props for each major component.
- Data dependencies for each component.
- Interaction states for bubble, filters, refresh, and dossier.
- Component boundaries: what fetches data vs what stays presentational.

## Acceptance Criteria

- The main view can be built without generic dashboard cards.
- Bubble interactions can open a meaningful coin dossier.
- Data freshness is visible in multiple risk-critical places.
- Components remain useful when backend data is empty or stale.
- The component design can support the later `02_DESIGN.md` visual system without rewrites.
